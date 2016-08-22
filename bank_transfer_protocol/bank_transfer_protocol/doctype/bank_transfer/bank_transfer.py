# -*- coding: utf-8 -*-
# Copyright (c) 2015, AptitudeTech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import datetime
from frappe.model.document import Document
from frappe.utils.file_manager import save_file
from erpnext.accounts.doctype.journal_entry.journal_entry import get_payment_entry_against_invoice
from erpnext.accounts.doctype.payment_request.payment_request import make_payment_entry
from erpnext.accounts.doctype.payment_entry.payment_entry import get_party_details
from erpnext.accounts.doctype.payment_entry.payment_entry import get_account_details
from erpnext.accounts.doctype.payment_entry.payment_entry import get_reference_details

class BankTransfer(Document):
	def validate(self):
		self.total_amount()

	def on_submit(self):
		bank_detail = frappe.get_doc("Bank Detail", self.bank_account)
		frappe.db.set_value("Bank Transfer", self.name, "file_creation_number", bank_detail.file_creation_number.zfill(4))
		frappe.db.set_value("Bank Transfer", self.name, "transfert_date", datetime.date.today())
		bank_detail.file_creation_number = str(int(bank_detail.file_creation_number) + 1)
		bank_detail.save()

	def total_amount(self):
		total = 0.0
		for d in self.get('items'):
                        total += d.grand_total
		self.total_transfer = total
	
	def download_test(self):
		str_save_file = "A"
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "originator_id").zfill(10)
		str_save_file += self.file_creation_number.zfill(4)
		
		today = datetime.date.today()
		
		str_save_file += "0" + today.strftime("%y%j")
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "destination_data_centre_code").zfill(5)
		
		str_save_file += "\nXC430"
		str_save_file += "0" + today.strftime("%y%j")
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "originators_short").ljust(15)
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "originators_long").ljust(30)
		str_save_file += "0"
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "institution_number").ljust(3)
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "branch_number").ljust(5)
		str_save_file += frappe.db.get_value("Bank Detail", self.bank_account, "account_number").ljust(12)

		count = 0
		total = 0.00
		for d in self.get('items'):
                	str_save_file += "\nC"
			str_save_file += "{:.2f}".format(d.grand_total).replace('.','').replace(',','').zfill(10)
			str_save_file += frappe.db.get_value("Bank Supplier Information", {'supplier':d.supplier_name}, "institution_number").zfill(3)
			str_save_file += frappe.db.get_value("Bank Supplier Information", {'supplier':d.supplier_name}, "branch_number").zfill(5)
			str_save_file += frappe.db.get_value("Bank Supplier Information", {'supplier':d.supplier_name}, "account_number").ljust(12)
			str_save_file += d.supplier_name.ljust(29)
			str_save_file += d.supplier_name.ljust(19)
			count += 1
			total += d.grand_total
		
		str_save_file += "\nYC" + str(count).zfill(8) + str(total).replace('.','').replace(',','').zfill(14)
		var_zero = 0
		str_save_file += "\nz" + str(var_zero).zfill(14) + str(var_zero).zfill(5) +  str(total).replace('.','').replace(',','').zfill(14) + str(count).zfill(5)

		save_file("file-bank-transfer.txt", str_save_file, self.doctype, self.name, is_private=True)

	def create_journal_entry(self):
		for d in self.get('items'):
			pme = frappe.new_doc("Payment Entry")
			paid_from_account_name = frappe.db.get_value("Bank Detail", self.bank_account, "account")
			company_name = frappe.db.get_value("Account", paid_from_account_name, "company")
			posting_date_today = datetime.date.today()
			party_details = get_party_details(company_name, "Supplier", d.supplier_name, posting_date_today)
			paid_from_account_detail = get_account_details(paid_from_account_name, posting_date_today)
			paid_to_account_detail = get_account_details(party_details["party_account"], posting_date_today)
			reference_detail = get_reference_details("Purchase Invoice", d.purchase_invoice, party_details["party_account_currency"])
	                json_update = {
				"naming_series": "PE-",
				"payment_type": "Pay",
				"party_type": "Supplier",
				"party": d.supplier_name,
				"posting_date": datetime.date.today(),
				"company" : company_name,
				"mode_of_payment": "Bank Transfer",
				"paid_from": paid_from_account_name,
				"paid_amount":d.grand_total,
				"paid_from_account_currency": party_details["party_account_currency"],
				"party_balance": party_details["party_balance"],
				"paid_to" : party_details["party_account"],
				"paid_to_account_currency": paid_to_account_detail["account_currency"],
				"paid_to_account_balance" : paid_to_account_detail["account_balance"],
				"received_amount" : d.grand_total,
				"reference_no" : self.file_creation_number,
				"reference_date" : posting_date_today,
				"references" : [{
					"reference_doctype": "Purchase Invoice",
					"reference_name": d.purchase_invoice,
					"due_date": reference_detail["due_date"],
					"total_amount": reference_detail["total_amount"],
					"outstanding_amount": reference_detail["outstanding_amount"],
					"allocated_amount": d.grand_total,
					"exchange_rate": reference_detail["exchange_rate"]
				}]
			}
			pme.update (json_update)
			#frappe.msgprint(str(json_update))
        	        pme.save()
                	#pme.submit()

			
