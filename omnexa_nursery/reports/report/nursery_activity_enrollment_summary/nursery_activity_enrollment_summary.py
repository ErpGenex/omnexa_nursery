# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["ae.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("ae.company = %(company)s")
		values["company"] = filters.company

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			ea.activity_name,
			ea.activity_type,
			ea.category,
			ae.status,
			COUNT(*) AS enrollment_count
		FROM `tabNursery Activity Enrollment` ae
		INNER JOIN `tabNursery Educational Activity` ea ON ea.name = ae.activity
		WHERE {where_clause}
		GROUP BY ea.name, ea.activity_name, ea.activity_type, ea.category, ae.status
		ORDER BY ea.activity_name, ae.status
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Activity"), "fieldname": "activity_name", "fieldtype": "Data", "width": 200},
		{"label": _("Type"), "fieldname": "activity_type", "fieldtype": "Data", "width": 160},
		{"label": _("Category"), "fieldname": "category", "fieldtype": "Data", "width": 120},
		{"label": _("Enrollment status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Count"), "fieldname": "enrollment_count", "fieldtype": "Int", "width": 90},
	]
