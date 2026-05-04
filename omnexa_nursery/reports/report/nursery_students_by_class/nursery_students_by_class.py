# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["ns.docstatus < 2"]
	values: dict = {"na": str(_("(No class)"))}

	if filters.get("company"):
		conditions.append("ns.company = %(company)s")
		values["company"] = filters.company
	if filters.get("status"):
		conditions.append("ns.status = %(status)s")
		values["status"] = filters.status

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			COALESCE(NULLIF(TRIM(ns.class_room), ''), %(na)s) AS class_room,
			ns.status,
			COUNT(*) AS student_count
		FROM `tabNursery Student` ns
		WHERE {where_clause}
		GROUP BY COALESCE(NULLIF(TRIM(ns.class_room), ''), %(na)s), ns.status
		ORDER BY class_room, ns.status
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Class / Room"), "fieldname": "class_room", "fieldtype": "Data", "width": 160},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 100},
	]
