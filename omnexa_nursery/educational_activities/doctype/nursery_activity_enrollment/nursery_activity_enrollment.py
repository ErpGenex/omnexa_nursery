# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class NurseryActivityEnrollment(Document):
	def validate(self):
		if not self.student or not self.activity:
			return
		filters = {"student": self.student, "activity": self.activity, "status": "Active"}
		if self.name:
			filters["name"] = ["!=", self.name]
		existing = frappe.db.get_value("Nursery Activity Enrollment", filters, "name")
		if existing:
			frappe.throw(
				_("Student is already enrolled in this activity ({0}).").format(existing),
				title=_("Duplicate Enrollment"),
			)
