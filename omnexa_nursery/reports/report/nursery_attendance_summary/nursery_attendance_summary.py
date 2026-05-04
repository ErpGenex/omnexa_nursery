# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["na.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("na.company = %(company)s")
		values["company"] = filters.company
	if filters.get("from_date"):
		conditions.append("na.attendance_date >= %(from_date)s")
		values["from_date"] = getdate(filters.get("from_date"))
	if filters.get("to_date"):
		conditions.append("na.attendance_date <= %(to_date)s")
		values["to_date"] = getdate(filters.get("to_date"))

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			na.attendance_date,
			na.status,
			COUNT(*) AS line_count
		FROM `tabNursery Attendance` na
		WHERE {where_clause}
		GROUP BY na.attendance_date, na.status
		ORDER BY na.attendance_date DESC, na.status
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Date"), "fieldname": "attendance_date", "fieldtype": "Date", "width": 120},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 110},
		{"label": _("Lines"), "fieldname": "line_count", "fieldtype": "Int", "width": 90},
	]
