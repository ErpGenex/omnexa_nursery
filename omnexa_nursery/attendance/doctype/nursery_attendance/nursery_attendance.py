# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NurseryAttendance(Document):
	def validate(self):
		if not self.student or not self.attendance_date or not self.company:
			return
		filters = {
			"student": self.student,
			"attendance_date": self.attendance_date,
			"company": self.company,
		}
		if self.name:
			filters["name"] = ["!=", self.name]
		existing = frappe.db.get_value("Nursery Attendance", filters, "name")
		if existing:
			frappe.throw(
				_("Attendance already exists for this student on this date ({0}).").format(existing),
				title=_("Duplicate Attendance"),
			)
