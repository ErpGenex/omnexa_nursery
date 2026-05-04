# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe


def before_install():
	if not frappe.db.a_row_exists("Company"):
		frappe.throw(
			"Create at least one Company before installing omnexa_nursery.",
			title="Prerequisite",
		)


def before_migrate():
	pass


def after_install():
	_ensure_roles()


def _ensure_roles():
	for role_name, desk in (
		("Nursery Administrator", 1),
		("Nursery Reception", 1),
		("Nursery Teacher", 1),
		("Nursery Accountant", 1),
		("Nursery Parent Portal", 0),
	):
		if frappe.db.exists("Role", role_name):
			continue
		r = frappe.new_doc("Role")
		r.role_name = role_name
		r.desk_access = desk
		r.is_custom = 1
		r.insert(ignore_permissions=True)
