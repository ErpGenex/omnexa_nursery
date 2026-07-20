# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["ns.docstatus < 2"]
	values: dict = {"na": str(_("(No age group)"))
	}

	if filters.get("company"):
		conditions.append("ns.company = %(company)s")
		values["company"] = filters.company

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			COALESCE(NULLIF(TRIM(ns.age_group), ''), %(na)s) AS age_group,
			ns.status,
			COUNT(*) AS student_count
		FROM `tabNursery Student` ns
		WHERE {where_clause}
		GROUP BY COALESCE(NULLIF(TRIM(ns.age_group), ''), %(na)s), ns.status
		ORDER BY age_group, ns.status
		""",
		values,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Age Group"), "fieldname": "age_group", "fieldtype": "Data", "width": 140
	},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 120
	},
		{"label": _("Students"), "fieldname": "student_count", "fieldtype": "Int", "width": 100
	},
	]
