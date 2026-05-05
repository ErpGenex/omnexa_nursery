# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import glob
import os

import frappe
from frappe.modules.import_file import import_file_by_path


def before_install():
	if not frappe.db.a_row_exists("Company"):
		frappe.throw(
			"Create at least one Company before installing omnexa_nursery.",
			title="Prerequisite",
		)


def before_migrate():
	pass


def after_migrate():
	"""Import script reports + base Workspace JSON. Desk KPIs/charts/layout: ``omnexa_core`` ``sync_workspace_for_app('omnexa_nursery')``."""
	_import_nursery_reports()
	_import_public_workspace()


def after_install():
	_ensure_roles()
	_import_nursery_reports()
	_import_public_workspace()


def _import_nursery_reports():
	"""Ensure Script Report rows exist before Workspace links validate (migrate module order is not guaranteed)."""
	app_root = frappe.get_app_path("omnexa_nursery")
	for path in sorted(glob.glob(os.path.join(app_root, "reports", "report", "*", "*.json"))):
		if os.path.isfile(path):
			import_file_by_path(path, force=True, ignore_version=True, reset_permissions=False)


def _import_public_workspace():
	"""Load Workspace from module path (Frappe sync only scans ``<module>/workspace/``)."""
	app_root = frappe.get_app_path("omnexa_nursery")
	ws_json = os.path.join(app_root, "nursery_setup", "workspace", "nursery", "nursery.json")
	if os.path.isfile(ws_json):
		import_file_by_path(ws_json, force=True, ignore_version=True, reset_permissions=False)


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
