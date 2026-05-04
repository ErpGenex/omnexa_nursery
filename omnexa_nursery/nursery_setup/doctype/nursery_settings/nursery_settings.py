# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe.model.document import Document


class NurserySettings(Document):
	def validate(self):
		if self.nursery_name and self.company:
			self.setup_complete = 1
