# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["ns.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("ns.company = %(company)s")
		values["company"] = filters.company

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			ns.status,
			COUNT(*) AS student_count
		FROM `tabNursery Student` ns
		WHERE {where_clause}
		GROUP BY ns.status
		ORDER BY student_count DESC, ns.status
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 140},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 100},
	]
