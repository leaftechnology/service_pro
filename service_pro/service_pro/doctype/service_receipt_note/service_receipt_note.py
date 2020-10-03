# -*- coding: utf-8 -*-
# Copyright (c) 2020, jan and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

class ServiceReceiptNote(Document):
	def change_status(self, status):
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET status=%s WHERE name=%s """,(status, self.name))
		frappe.db.commit()

	def on_submit(self):
		for i in self.materials:
			for ii in range(0,i.qty):
				doc = {
					"doctype": "Inspection",
					"date": self.date,
					"customer": self.customer,
					"customer_name": self.customer_name,
					"city": self.city,
					"contact_person": self.contact_person,
					"telephone": self.telephone,
					"fax": self.fax,
					"machine_type": self.machine_type,
					"manufacture": self.manufacture,
					"serial_no": self.serial_no,
					"power": self.power,
					"speed": self.speed,
					"frequency": self.frequency,
					"volts": self.volts,
					"current": self.current,
					"item_code": i.materials,
					"item_name": i.item_name,
					"qty": 1,
					"service_receipt_note": self.name
				}

				frappe.get_doc(doc).insert()

	def submit_inspections(self):
		inspections = frappe.db.sql(""" SELECT * FROM `tabInspection` WHERE service_receipt_note=%s""",self.name, as_dict=1)
		for inspection in inspections:
			record = frappe.get_doc("Inspection", inspection.name)
			record.submit()
		frappe.msgprint("Done Submitting Inspections")

	def submit_estimations(self):
			estimations = frappe.db.sql(""" SELECT * FROM `tabEstimation` WHERE service_receipt_note=%s""",self.name, as_dict=1)
			for estimation in estimations:
				record = frappe.get_doc("Estimation", estimation.name)
				record.submit()
			frappe.msgprint("Done Submitting Estimation")


	def create_quotation(self):
		doc = {
			"doctype": "Quotation",
			"party_name": self.customer,
			"service_receipt_note": self.name,
			"items": self.get_items()
		}

		doc_q = frappe.get_doc(doc).insert()
		frappe.db.sql(""" UPDATE `tabService Receipt Note` SET quotation=%s WHERE name=%s""",(doc_q.name,self.name), as_dict=1)
		frappe.db.commit()
		return doc_q.name
	def get_items(self):
		items = []
		for item in self.materials:
			inspection_values = frappe.db.get_value('Estimation',
													{"service_receipt_note": self.name, "item_code": item.materials},
													['rate','amount'], as_dict=1)
			item_record = frappe.db.sql(""" SELECT * FROM `tabItem` WHERE name=%s""", item.materials, as_dict=1)
			print("ITEEEEEEEEEEEEM")
			print(item_record)
			items.append({
				"item_code": item.materials,
				"item_name": item_record[0].item_name,
				"description": item_record[0].description,
				"qty": item.qty,
				"rate": inspection_values.rate,
				"amount": inspection_values.amount,
				"uom": item_record[0].default_unit_of_measure,

			})
		return items


@frappe.whitelist()
def make_quotation(source_name, target_doc=None, skip_item_mapping=False):
	# def set_missing_values(source, target):
	# 	target.ignore_pricing_rule = 1
	# 	target.run_method("set_missing_values")
	# 	target.run_method("set_po_nos")
	# 	target.run_method("calculate_taxes_and_totals")
    #
	# 	if source.company_address:
	# 		target.update({'company_address': source.company_address})
	# 	else:
	# 		# set company address
	# 		target.update(get_company_address(target.company))
    #
	# 	if target.company_address:
	# 		target.update(get_fetch_values("Delivery Note", 'company_address', target.company_address))

	# def update_item(source, target, source_parent):
	# 	target.base_amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.base_rate)
	# 	target.amount = (flt(source.qty) - flt(source.delivered_qty)) * flt(source.rate)
	# 	target.qty = flt(source.qty) - flt(source.delivered_qty)
    #
	# 	item = get_item_defaults(target.item_code, source_parent.company)
	# 	item_group = get_item_group_defaults(target.item_code, source_parent.company)
    #
	# 	if item:
	# 		target.cost_center = frappe.db.get_value("Project", source_parent.project, "cost_center") \
	# 			or item.get("buying_cost_center") \
	# 			or item_group.get("buying_cost_center")

	mapper = {
		"Service Receipt Note": {
			"doctype": "Quotation",
			"validation": {
				"docstatus": ["=", 1]
			},
			"field_map": {
				"customer": "party_name"
			}
		},
	}

	mapper["Service Receipt Note Item"] = {
		"doctype": "Quotation Item",
		"field_map": {
			"materials": "item_code",
			"qty": "qty",
		},

	}

	target_doc = get_mapped_doc("Service Receipt Note", source_name, mapper, target_doc)

	return target_doc