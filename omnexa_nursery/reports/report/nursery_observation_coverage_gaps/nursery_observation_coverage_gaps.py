# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns

from omnexa_core.omnexa_core.report_print.report_query_filters import (
	get_all_filters,
	policy_version_filters,
	prepare_filters,
	sql_conditions,
)



def execute(filters=None):
	columns = [
		{"label": _("Student"), "fieldname": "student_id", "fieldtype": "Link", "options": "Nursery Student", "width": 130},
		{"label": _("Name (EN)"), "fieldname": "full_name_en", "fieldtype": "Data", "width": 180},
		{"label": _("Class / Room"), "fieldname": "class_room", "fieldtype": "Data", "width": 120},
		{"label": _("Last observation"), "fieldname": "last_observation_date", "fieldtype": "Date", "width": 130},
		{"label": _("Days since"), "fieldname": "days_since_observation", "fieldtype": "Int", "width": 100},
	]
	filters = prepare_filters(filters)
	conditions, params = sql_conditions(filters, "Nursery Student", date_field="creation", company=True, branch=True)
	rows = frappe.db.sql(
		f"""
		SELECT
			ns.name AS student_id,
			ns.full_name_en,
			ns.class_room,
			MAX(ndo.log_date) AS last_observation_date,
			DATEDIFF(%(as_of)s, MAX(ndo.log_date)) AS days_since_observation
		FROM `tabNursery Student`
		WHERE {' AND '.join(conditions)}
		GROUP BY ns.name, ns.full_name_en, ns.class_room
		HAVING MAX(ndo.log_date) IS NULL
			OR DATEDIFF(%(as_of)s, MAX(ndo.log_date)) > %(min_gap)s
		ORDER BY last_observation_date IS NULL DESC,
			days_since_observation DESC,
			ns.class_room,
			ns.full_name_en
		""",
		params,
		as_dict=True,
	)
	chart = auto_chart_for_columns(rows, columns)
	return columns, rows, None, chart