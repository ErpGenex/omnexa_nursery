# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _

from omnexa_core.omnexa_core.utils.report_charts import auto_chart_for_columns


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["tr.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("tr.company = %(company)s")
		values["company"] = filters.company

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			tr.name AS route_id,
			tr.route_name,
			tr.vehicle,
			tr.driver,
			tr.supervisor,
			tr.pickup_time,
			tr.drop_time,
			tr.notes
		FROM `tabNursery Transport` tr
		WHERE {where_clause}
		ORDER BY tr.route_name, tr.name
		""",
		values,
		as_dict=True,
	)
	columns = _columns()
	chart = auto_chart_for_columns(data, columns)
	return columns, data, None, chart


def _columns():
	return [
		{"label": _("Route Doc"), "fieldname": "route_id", "fieldtype": "Link", "options": "Nursery Transport", "width": 140
	},
		{"label": _("Route"), "fieldname": "route_name", "fieldtype": "Data", "width": 160
	},
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Data", "width": 120
	},
		{"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Employee", "width": 140
	},
		{"label": _("Supervisor"), "fieldname": "supervisor", "fieldtype": "Link", "options": "Employee", "width": 140
	},
		{"label": _("Pickup"), "fieldname": "pickup_time", "fieldtype": "Time", "width": 90
	},
		{"label": _("Drop-off"), "fieldname": "drop_time", "fieldtype": "Time", "width": 90
	},
		{"label": _("Notes"), "fieldname": "notes", "fieldtype": "Small Text", "width": 200
	},
	]
