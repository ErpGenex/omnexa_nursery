# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.utils import getdate


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["obs.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("obs.company = %(company)s")
		values["company"] = filters.company
	if filters.get("from_date"):
		conditions.append("obs.log_date >= %(from_date)s")
		values["from_date"] = getdate(filters.get("from_date"))
	if filters.get("to_date"):
		conditions.append("obs.log_date <= %(to_date)s")
		values["to_date"] = getdate(filters.get("to_date"))

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			obs.log_date,
			COALESCE(NULLIF(TRIM(obs.eating_status), ''), %(eat_na)s) AS eating_status,
			COALESCE(NULLIF(TRIM(obs.nap_status), ''), %(nap_na)s) AS nap_status,
			COUNT(*) AS observation_count
		FROM `tabNursery Daily Observation` obs
		WHERE {where_clause}
		GROUP BY obs.log_date,
			COALESCE(NULLIF(TRIM(obs.eating_status), ''), %(eat_na)s),
			COALESCE(NULLIF(TRIM(obs.nap_status), ''), %(nap_na)s)
		ORDER BY obs.log_date DESC, eating_status, nap_status
		""",
		{
			**values,
			"eat_na": str(_("(Not recorded)")),
			"nap_na": str(_("(Not recorded)")),
		},
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Date"), "fieldname": "log_date", "fieldtype": "Date", "width": 120},
		{"label": _("Eating"), "fieldname": "eating_status", "fieldtype": "Data", "width": 110},
		{"label": _("Nap"), "fieldname": "nap_status", "fieldtype": "Data", "width": 110},
		{"label": _("Observations"), "fieldname": "observation_count", "fieldtype": "Int", "width": 110},
	]
