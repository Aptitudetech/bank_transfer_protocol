// Copyright (c) 2016, AptitudeTech and contributors
// For license information, please see license.txt

/*frappe.ui.form.on('Bank Transfer Item', 'purchase_invoice', function(frm) { 
		add_fetch('purchase_invoice', 'supplier_name', 'supplier_name'); 
	});*/

/*frappe.ui.form.on('Bank Transfer', {
	refresh: function(frm) {
		add_fetch('purchase_invoice', 'supplier_name', 'customer_name');
	}

});*/

/*frappe.ui.form.on("Bank Transfer Item", "purchase_invoice",
    function(frm, cdt, cdn) {
        frappe.call({
            "method": "frappe.client.get",
            args: {
                doctype: "Purchase Invoice",
                name: locals[cdt][cdn].purchase_invoice
            },
            callback: function (data) {
                frappe.model.set_value(cdt,cdn, "supplier_name",
                    data.message.supplier_name)
		
            }
        })
    });*/

frappe.ui.form.on("Bank Transfer", "refresh", function(frm) {
    if(frm.doc.docstatus == 1){
    	frm.add_custom_button(__("Generate Transfer Bank File"), function() {
            // When this button is clicked, do this
		frm.call({
        		'method': 'download_test',
			'doc': frm.doc,
        		'args': {},
    		
			callback: function() {
				cur_frm.reload_doc();
			}
		});
            });
	}
    });



frappe.ui.form.on("Bank Transfer", "refresh", function(frm) {
    if(frm.doc.docstatus == 1){
        frm.add_custom_button(__("Make Payment Entry"), function() {
            // When this button is clicked, do this
                frm.call({
                        'method': 'create_journal_entry',
                        'doc': frm.doc,
                        'args': {},

                        callback: function() {
				frappe.set_route("List", "Payment Entry");
                        }
                });
            });
        }
    });


frappe.ui.form.on("Bank Transfer Item", "purchase_invoice",
    function(frm, cdt, cdn) {
        frappe.call({
            "method": "frappe.client.get_value",
            args: {
                doctype: "Purchase Invoice",
		fieldname: ["supplier_name", "grand_total"],
		filters: {name: locals[cdt][cdn].purchase_invoice}
            },
            callback: function (data) {
		Object.keys(data.message).forEach(function(field){
        		frappe.model.set_value(cdt, cdn, field, data.message[field]);
   		});
            }
        })
    });

frappe.ui.form.on("Bank Transfer Item", "grand_total", function(frm, cdt, cdn){
    frm.call({
        'method': 'total_amount',
        'doc': frm.doc,
        'args': {}
    });
});

/*cur_frm.fields_dict['customer_group'].get_query = function(doc, dt, dn) {
	return{
		filters:{'is_group': 'No'}
	}
}*/
