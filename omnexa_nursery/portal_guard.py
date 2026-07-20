# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Restrict nursery portal users to allowed desk routes and APIs."""

from __future__ import annotations

import json

import frappe
from frappe import _

PARENT_PORTAL_ROLE = "Nursery Parent Portal"
STAFF_NURSERY_ROLES = frozenset({"Nursery Manager", "Nursery User", "System Manager"})

PORTAL_HOME_ROUTES: dict[str, str] = {
	PARENT_PORTAL_ROLE: "/app/nursery-parent-portal",
}

PORTAL_WORKSPACE_SPECS: dict[str, dict] = {
	PARENT_PORTAL_ROLE: {
		"name": "nursery-ws-parent",
		"title": "Nursery Parent Hub",
		"label": "Parent Portal",
		"icon": "nursery-parent",
	},
}

PARENT_ALLOWED_PAGES = frozenset(
	{
		"nursery-parent-portal",
	}
)

PARENT_ALLOWED_DOCTYPES = frozenset(
	{
		"nursery-child",
		"nursery-enrollment",
		"nursery-attendance",
		"nursery-fee-invoice",
	}
)


def portal_role_for_user(user: str | None = None) -> str | None:
	user = user or frappe.session.user
	if not user or user == "Guest":
		return None
	roles = set(frappe.get_roles(user))
	if PARENT_PORTAL_ROLE in roles and not roles & STAFF_NURSERY_ROLES:
		return PARENT_PORTAL_ROLE
	return None


def portal_allowed_pages(role: str | None) -> frozenset[str]:
	if role == PARENT_PORTAL_ROLE:
		return PARENT_ALLOWED_PAGES
	return frozenset()


def portal_allowed_doctypes(role: str | None) -> frozenset[str]:
	if role == PARENT_PORTAL_ROLE:
		return PARENT_ALLOWED_DOCTYPES
	return frozenset()


def portal_home_route(user: str | None = None) -> str | None:
	role = portal_role_for_user(user)
	return PORTAL_HOME_ROUTES.get(role or "") if role else None


def extend_bootinfo(bootinfo):
	"""Expose portal restrictions to desk JS."""
	role = portal_role_for_user()
	if not role:
		return
	bootinfo.nursery_portal = {
		"portal_only": True,
		"portal_role": role,
		"home_route": PORTAL_HOME_ROUTES[role],
		"allowed_pages": sorted(portal_allowed_pages(role)),
		"allowed_doctypes": sorted(portal_allowed_doctypes(role)),
	}


def ensure_nursery_workspace_portal_roles() -> dict:
	"""Hide full Nursery workspace from portal users; add minimal parent workspace."""
	from omnexa_nursery.api.nursery_role_demo import NURSERY_STAFF_ROLES

	stats = {"nursery_roles_set": 0, "parent_ws": False}
	staff_roles = [r for r in NURSERY_STAFF_ROLES if frappe.db.exists("Role", r)]

	if frappe.db.exists("Workspace", "Nursery"):
		ws = frappe.get_doc("Workspace", "Nursery")
		ws.set("roles", [])
		for role in staff_roles:
			ws.append("roles", {"role": role})
		ws.flags.ignore_permissions = True
		ws.save()
		stats["nursery_roles_set"] = len(staff_roles)
		frappe.db.commit()

	try:
		stats["parent_ws"] = _ensure_portal_workspace(
			PARENT_PORTAL_ROLE,
			[
				("Page", "nursery-parent-portal", "Parent Portal"),
				("DocType", "Nursery Child", "My Children"),
				("DocType", "Nursery Enrollment", "Enrollments"),
				("DocType", "Nursery Attendance", "Attendance"),
				("DocType", "Nursery Fee Invoice", "Invoices"),
			],
		)
	except Exception as exc:
		stats["parent_ws_error"] = str(exc)[:200]
	frappe.clear_cache(doctype="Workspace")
	return stats


def _ensure_portal_workspace(role: str, links: list[tuple]) -> bool:
	if not frappe.db.exists("Role", role):
		return False
	spec = PORTAL_WORKSPACE_SPECS[role]
	name = spec["name"]
	if frappe.db.exists("Workspace", name):
		ws = frappe.get_doc("Workspace", name)
	else:
		ws = frappe.new_doc("Workspace")
		ws.update(
			{
				"name": name,
				"label": spec["label"],
				"title": spec["title"],
				"module": "Nursery Setup",
				"icon": spec["icon"],
				"public": 0,
				"is_hidden": 0,
			}
		)
	ws.set("roles", [])
	ws.append("roles", {"role": role})
	ws.set("links", [])
	for link_type, link_to, link_label in links:
		ws.append(
			"links",
			{
				"type": "Link",
				"link_type": link_type,
				"link_to": link_to,
				"label": link_label,
				"hidden": 0,
				"onboard": 0,
				"is_query_report": 0,
			},
		)
	shortcuts = []
	content = [{"id": "hdr", "type": "header", "data": {"text": f"<b>{spec['label']}</b>", "col": 12}}]
	for idx, (_lt, link_to, link_label) in enumerate(links):
		shortcuts.append(
			{
				"type": "DocType" if _lt == "DocType" else "Page",
				"link_to": link_to,
				"label": link_label,
				"color": "Blue",
			}
		)
		content.append(
			{
				"id": f"sc{idx}",
				"type": "shortcut",
				"data": {"shortcut_name": link_label, "col": 4},
			}
		)
	ws.shortcuts = []
	for sc in shortcuts:
		ws.append("shortcuts", sc)

	ws.content = json.dumps(content, separators=(",", ":"))
	ws.flags.ignore_permissions = True
	if ws.is_new():
		ws.insert()
	else:
		ws.save()
	return True
