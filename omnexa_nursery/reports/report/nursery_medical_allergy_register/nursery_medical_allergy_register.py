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

	include_all = filters.get("include_all_students") in (1, True, "1")
	if not include_all:
		conditions.append(
			"(IFNULL(ns.allergies, '') != '' OR IFNULL(ns.blood_group, '') != '')"
		)

	where_clause = " AND ".join(conditions)
	data = frappe.db.sql(
		f"""
		SELECT
			ns.name AS student_id,
			ns.full_name_en,
			ns.full_name_ar,
			ns.class_room,
			ns.age_group,
			ns.status,
			ns.allergies,
			ns.blood_group,
			ns.emergency_contact_name,
			ns.emergency_contact_phone,
			par.phone_1 AS parent_phone_1,
			par.phone_2 AS parent_phone_2,
			par.whatsapp AS parent_whatsapp
		FROM `tabNursery Student` ns
		LEFT JOIN `tabNursery Parent Profile` par ON par.name = ns.primary_parent
		WHERE {where_clause}
		ORDER BY ns.class_room, ns.full_name_en
		""",
		values,
		as_dict=True,
	)

	return _columns(), data


def _columns():
	return [
		{"label": _("Student"), "fieldname": "student_id", "fieldtype": "Link", "options": "Nursery Student", "width": 130},
		{"label": _("Name (EN)"), "fieldname": "full_name_en", "fieldtype": "Data", "width": 160},
		{"label": _("Name (AR)"), "fieldname": "full_name_ar", "fieldtype": "Data", "width": 140},
		{"label": _("Class / Room"), "fieldname": "class_room", "fieldtype": "Data", "width": 120},
		{"label": _("Age Group"), "fieldname": "age_group", "fieldtype": "Data", "width": 90},
		{"label": _("Status"), "fieldname": "status", "fieldtype": "Data", "width": 100},
		{"label": _("Allergies"), "fieldname": "allergies", "fieldtype": "Small Text", "width": 200},
		{"label": _("Blood Group"), "fieldname": "blood_group", "fieldtype": "Data", "width": 90},
		{"label": _("Emergency Name"), "fieldname": "emergency_contact_name", "fieldtype": "Data", "width": 140},
		{"label": _("Emergency Phone"), "fieldname": "emergency_contact_phone", "fieldtype": "Data", "width": 120},
		{"label": _("Parent Phone 1"), "fieldname": "parent_phone_1", "fieldtype": "Data", "width": 120},
		{"label": _("Parent Phone 2"), "fieldname": "parent_phone_2", "fieldtype": "Data", "width": 120},
		{"label": _("WhatsApp"), "fieldname": "parent_whatsapp", "fieldtype": "Data", "width": 110},
	]
