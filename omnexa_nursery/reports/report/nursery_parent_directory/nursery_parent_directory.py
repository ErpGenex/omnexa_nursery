# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe
from frappe import _


def execute(filters=None):
	filters = frappe._dict(filters or {})
	conditions = ["par.docstatus < 2"]
	values: dict = {}

	if filters.get("company"):
		conditions.append("par.company = %(company)s")
		values["company"] = filters.company

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			par.name AS parent_id,
			par.father_name,
			par.mother_name,
			par.phone_1,
			par.phone_2,
			par.whatsapp,
			par.email,
			par.address,
			par.customer AS billing_customer
		FROM `tabNursery Parent Profile` par
		WHERE {where_clause}
		ORDER BY par.father_name, par.name
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Parent"), "fieldname": "parent_id", "fieldtype": "Link", "options": "Nursery Parent Profile", "width": 140},
		{"label": _("Father"), "fieldname": "father_name", "fieldtype": "Data", "width": 160},
		{"label": _("Mother"), "fieldname": "mother_name", "fieldtype": "Data", "width": 160},
		{"label": _("Phone 1"), "fieldname": "phone_1", "fieldtype": "Data", "width": 120},
		{"label": _("Phone 2"), "fieldname": "phone_2", "fieldtype": "Data", "width": 120},
		{"label": _("WhatsApp"), "fieldname": "whatsapp", "fieldtype": "Data", "width": 120},
		{"label": _("Email"), "fieldname": "email", "fieldtype": "Data", "width": 180},
		{"label": _("Address"), "fieldname": "address", "fieldtype": "Small Text", "width": 220},
		{"label": _("Billing customer"), "fieldname": "billing_customer", "fieldtype": "Link", "options": "Customer", "width": 160},
	]
