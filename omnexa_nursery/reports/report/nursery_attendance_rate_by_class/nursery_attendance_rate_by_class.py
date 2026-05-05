# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["na.docstatus < 2", "ns.docstatus < 2"]
	values: dict = {"nc": str(_("(No class)"))}

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
	rows = frappe.db.sql(
		f"""
		SELECT
			COALESCE(NULLIF(TRIM(ns.class_room), ''), %(nc)s) AS class_room,
			SUM(CASE WHEN na.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
			COUNT(*) AS total_count
		FROM `tabNursery Attendance` na
		INNER JOIN `tabNursery Student` ns ON ns.name = na.student
		WHERE {where_clause}
		GROUP BY COALESCE(NULLIF(TRIM(ns.class_room), ''), %(nc)s)
		ORDER BY class_room
		""",
		values,
		as_dict=True,
	)

	for r in rows:
		total = r.get("total_count") or 0
		present = r.get("present_count") or 0
		r["attendance_rate_pct"] = flt((present / total) * 100.0, 2) if total else 0.0

	return _columns(), rows


def _columns():
	return [
		{"label": _("Class / Room"), "fieldname": "class_room", "fieldtype": "Data", "width": 160},
		{"label": _("Present"), "fieldname": "present_count", "fieldtype": "Int", "width": 90},
		{"label": _("Total lines"), "fieldname": "total_count", "fieldtype": "Int", "width": 100},
		{"label": _("Present %"), "fieldname": "attendance_rate_pct", "fieldtype": "Float", "width": 100},
	]
