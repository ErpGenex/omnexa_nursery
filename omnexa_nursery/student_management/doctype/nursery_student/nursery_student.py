# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import date_diff, getdate, today


class NurseryStudent(Document):
	def validate(self):
		if self.name:
			self.student_id = self.name
		if self.birth_date:
			d0 = getdate(self.birth_date)
			d1 = getdate(today())
			if d0 > d1:
				frappe.throw(_("Birth date cannot be in the future."), title=_("Nursery Student"))
			self.age_years = int(date_diff(d1, d0) / 365.25)
		else:
			self.age_years = 0
