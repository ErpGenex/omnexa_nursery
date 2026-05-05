# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import cint, getdate, today


def execute(filters=None):
	filters = frappe._dict(filters or {})
	if not filters.get("company"):
		frappe.throw(_("Company is required."), title=_("Filters"))

	as_of = getdate(filters.get("as_of") or today())
	min_gap = max(0, cint(filters.get("min_gap_days") or 7))

	values = {"company": filters.company, "as_of": as_of, "min_gap": min_gap}

	data = frappe.db.sql(
		"""
		SELECT
			ns.name AS student_id,
			ns.full_name_en,
			ns.class_room,
			MAX(ndo.log_date) AS last_observation_date,
			DATEDIFF(%(as_of)s, MAX(ndo.log_date)) AS days_since_observation
		FROM `tabNursery Student` ns
		LEFT JOIN `tabNursery Daily Observation` ndo
			ON ndo.student = ns.name AND ndo.docstatus < 2
		WHERE ns.docstatus < 2
			AND ns.status = 'Active'
			AND ns.company = %(company)s
		GROUP BY ns.name, ns.full_name_en, ns.class_room
		HAVING MAX(ndo.log_date) IS NULL
			OR DATEDIFF(%(as_of)s, MAX(ndo.log_date)) > %(min_gap)s
		ORDER BY last_observation_date IS NULL DESC,
			days_since_observation DESC,
			ns.class_room,
			ns.full_name_en
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Student"), "fieldname": "student_id", "fieldtype": "Link", "options": "Nursery Student", "width": 130},
		{"label": _("Name (EN)"), "fieldname": "full_name_en", "fieldtype": "Data", "width": 180},
		{"label": _("Class / Room"), "fieldname": "class_room", "fieldtype": "Data", "width": 120},
		{"label": _("Last observation"), "fieldname": "last_observation_date", "fieldtype": "Date", "width": 130},
		{"label": _("Days since"), "fieldname": "days_since_observation", "fieldtype": "Int", "width": 100},
	]
