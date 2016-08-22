# -*- coding: utf-8 -*-
# Copyright (c) 2015, AptitudeTech and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class BankSupplierInformation(Document):
	def get_supplier_name(self):
		self.supplier_name = frappe.db.get_value("Supplier", self.supplier, "supplier_name")

