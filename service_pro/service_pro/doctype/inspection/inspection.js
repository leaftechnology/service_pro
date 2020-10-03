// Copyright (c) 2020, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Inspection', {
    onload: function () {
      if(cur_frm.is_new() && cur_frm.doc.service_receipt_note){
cur_frm.trigger("service_receipt_note")
      }
    },
    service_receipt_note: function () {
      if(cur_frm.is_new() && cur_frm.doc.service_receipt_note){
          frappe.db.get_doc("Service Receipt Note", cur_frm.doc.service_receipt_note)
            .then(doc => {
                var fields = [
                    "customer","customer_name",
                    "city", "contact_person",
                    "telephone", "fax", "machine_type", "manufacture", "serial_no", "power",
                    "speed", "frequency", "volts", "current"
                ]
                  for(var i=0;i<fields.length;i+=1){
                    cur_frm.doc[fields[i]] = doc[fields[i]]
                    cur_frm.refresh_field(fields[i])
                  }

            })
      }
    },
     customer: function () {
	    if(cur_frm.doc.customer){
	         frappe.db.get_doc("Customer", cur_frm.doc.customer)
            .then(doc => {
                cur_frm.doc.customer_name = doc.customer_name
                cur_frm.refresh_field("customer_name")
            })
        }

    },
    refresh: function (frm) {
        cur_frm.set_query('service_receipt_note', () => {
            return {
                filters: [
                    ["docstatus", "=", 1],
                    ["status", "=", "To Inspection"]
                ]
            }
        })
        if(cur_frm.doc.docstatus && !(["Closed", "Completed"].includes(cur_frm.doc.status))){
            console.log("WALA MAN")
             frm.add_custom_button(__("Close"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "Closed"
                        },
                        freeze: true,
                        freeze_message: "Closing...",
                        callback: () => {
                            cur_frm.reload_doc()
                        }
                })
            })
        } else if (cur_frm.doc.status === "Closed"){
            frm.add_custom_button(__("Open"), () => {
                    cur_frm.call({
                        doc: cur_frm.doc,
                        method: 'change_status',
                        args: {
                            status: "To Estimation"
                        },
                        freeze: true,
                        freeze_message: "Opening...",
                        callback: () => {
                        cur_frm.reload_doc()
                        }
                })
            })
        }
    }
});


cur_frm.cscript.item_code = function (frm, cdt, cdn) {
    var d = locals[cdt][cdn]
     frappe.db.get_doc("Item", d.item_code)
            .then(doc => {
               d.item_name = doc.item_name
                cur_frm.refresh_field("item_name")
            })
}
