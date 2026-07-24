# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import json
import os

import frappe
from frappe.modules.import_file import import_file_by_path


def before_migrate():
	pass


def after_migrate():
	"""Import script reports + base Workspace JSON. Desk KPIs/charts/layout: ``omnexa_core`` ``sync_workspace_for_app('omnexa_nursery')``."""
	_import_workspace_artifacts()
	# JSON import runs after omnexa_core's migrate-time desk sync and overwrites Workspace.content
	# with the static header from nursery.json — re-apply control tower so shortcuts/KPIs/links render.
	_sync_nursery_workspace_from_control_tower()


def after_install():
	_ensure_roles()
	_import_workspace_artifacts()
	_sync_nursery_workspace_from_control_tower()


def _import_workspace_artifacts():
	"""Import workspace-related JSON files before sync so links do not get pruned."""
	app_root = frappe.get_app_path("omnexa_nursery")
	target_dirs = {"page", "report", "workspace", "onboarding_step", "module_onboarding"}
	json_paths: list[str] = []

	for root, _dirs, files in os.walk(app_root):
		parts = {part.lower() for part in root.split(os.sep)}
		if not parts.intersection(target_dirs):
			continue
		for filename in files:
			if filename.endswith(".json"):
				json_paths.append(os.path.join(root, filename))

	for path in sorted(json_paths):
		with open(path, encoding="utf-8") as handle:
			payload = json.load(handle) or {}
		if isinstance(payload, dict) and payload.get("name") and not payload.get("doctype") and "/workspace/" in path.replace("\\", "/"):
			payload = _sanitize_workspace_payload(payload)
			if frappe.db.exists("Workspace", payload["name"]):
				workspace = frappe.get_doc("Workspace", payload["name"])
				workspace.update(payload)
				workspace.save(ignore_permissions=True)
			else:
				payload["doctype"] = "Workspace"
				frappe.get_doc(payload).insert(ignore_permissions=True)
			continue
		import_file_by_path(path, force=True, ignore_version=True, reset_permissions=False)


def _sync_nursery_workspace_from_control_tower():
	try:
		from omnexa_core.omnexa_core.workspace_control_tower import sync_workspace_for_app

		sync_workspace_for_app("omnexa_nursery")
	except Exception:
		frappe.log_error("omnexa_nursery: sync_workspace_for_app failed", frappe.get_traceback())


def _workspace_target_exists(link_type: str | None, link_to: str | None) -> bool:
	if not link_type or not link_to:
		return False
	if link_type == "DocType":
		return bool(frappe.db.exists("DocType", link_to))
	if link_type == "Report":
		return bool(frappe.db.exists("Report", link_to))
	if link_type == "Page":
		return bool(frappe.db.exists("Page", link_to))
	return True


def _sanitize_workspace_payload(payload: dict) -> dict:
	clean = dict(payload)
	links = []
	for row in clean.get("links", []) or []:
		if row.get("type") == "Link" and not _workspace_target_exists(row.get("link_type"), row.get("link_to")):
			continue
		links.append(row)
	clean["links"] = links

	shortcuts = []
	for row in clean.get("shortcuts", []) or []:
		if row.get("type") in {"DocType", "Report", "Page"} and not _workspace_target_exists(row.get("type"), row.get("link_to")):
			continue
		shortcuts.append(row)
	clean["shortcuts"] = shortcuts
	return clean


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
