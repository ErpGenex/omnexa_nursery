# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import json
import os

import frappe
from frappe import _
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
	"""Import script reports, workspace, then desk KPIs/charts (``migrate`` may run modules in any order)."""
	_import_nursery_reports()
	_import_public_workspace()
	_ensure_nursery_desk_artifacts()
	_patch_nursery_workspace_desk()


def after_install():
	_ensure_roles()
	_import_public_workspace()
	# KPIs/charts/reports are applied in ``after_migrate`` once Report rows exist.


def _import_nursery_reports():
	"""Ensure Script Report rows exist before Workspace links validate against them."""
	app_root = frappe.get_app_path("omnexa_nursery")
	for slug in ("nursery_students_by_class", "nursery_attendance_summary"):
		path = os.path.join(app_root, "reports", "report", slug, f"{slug}.json")
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


def _ensure_nursery_desk_artifacts():
	"""Number cards + Group By charts for the Nursery workspace (not synced as JSON in this app)."""
	if not frappe.db.exists("DocType", "Nursery Student"):
		return

	for label, dt in (
		("Nursery Students", "Nursery Student"),
		("Nursery Parents", "Nursery Parent Profile"),
		("Nursery Attendance Records", "Nursery Attendance"),
	):
		if frappe.db.exists("Number Card", label):
			continue
		nc = frappe.new_doc("Number Card")
		nc.label = label
		nc.type = "Document Type"
		nc.document_type = dt
		nc.function = "Count"
		nc.filters_json = "[]"
		nc.module = "Reports"
		nc.is_public = 1
		nc.is_standard = 0
		nc.insert(ignore_permissions=True)

	charts = (
		(
			"Nursery Students by Status",
			{
				"chart_type": "Group By",
				"document_type": "Nursery Student",
				"group_by_type": "Count",
				"group_by_based_on": "status",
				"timeseries": 0,
				"type": "Donut",
				"filters_json": "[]",
			},
		),
		(
			"Nursery Attendance by Status",
			{
				"chart_type": "Group By",
				"document_type": "Nursery Attendance",
				"group_by_type": "Count",
				"group_by_based_on": "status",
				"timeseries": 0,
				"type": "Donut",
				"filters_json": "[]",
			},
		),
	)

	for chart_name, fields in charts:
		if frappe.db.exists("Dashboard Chart", chart_name):
			continue
		dc = frappe.new_doc("Dashboard Chart")
		dc.chart_name = chart_name
		dc.module = "Reports"
		dc.is_public = 1
		dc.is_standard = 0
		dc.update(fields)
		dc.insert(ignore_permissions=True)


def _patch_nursery_workspace_desk():
	"""Add KPI cards, charts, and report shortcuts to the public Nursery workspace."""
	if not frappe.db.exists("Workspace", "Nursery"):
		return

	ws = frappe.get_doc("Workspace", "Nursery")

	ws.set(
		"number_cards",
		[
			{"number_card_name": "Nursery Students", "label": _("Students")},
			{"number_card_name": "Nursery Parents", "label": _("Parents")},
			{"number_card_name": "Nursery Attendance Records", "label": _("Attendance lines")},
		],
	)

	ws.set(
		"charts",
		[
			{"chart_name": "Nursery Students by Status", "label": _("Students by status")},
			{"chart_name": "Nursery Attendance by Status", "label": _("Attendance mix")},
		],
	)

	ws.set(
		"shortcuts",
		[
			{
				"type": "DocType",
				"link_to": "Nursery Settings",
				"doc_view": "",
				"label": _("Nursery Settings"),
				"icon": "setting",
				"color": "Blue",
			},
			{
				"type": "DocType",
				"link_to": "Nursery Student",
				"doc_view": "List",
				"label": _("Students"),
				"icon": "list",
				"color": "Green",
			},
			{
				"type": "Report",
				"link_to": "Nursery Students by Class",
				"label": "Students by class",
				"icon": "file",
				"color": "Cyan",
			},
			{
				"type": "Report",
				"link_to": "Nursery Attendance Summary",
				"label": "Attendance summary",
				"icon": "calendar",
				"color": "Orange",
			},
		],
	)

	blocks = [
		{
			"id": "nur-h1",
			"type": "header",
			"data": {
				"text": '<div class="text-muted">'
				+ _("Nursery management: children, parents, activities, attendance, and billing.")
				+ " <b>"
				+ _("Nursery Settings")
				+ "</b> "
				+ _("first.")
				+ "</div>",
				"col": 12,
			},
		},
		{"id": "nur-kpi-h", "type": "header", "data": {"text": "<b>" + _("KPIs") + "</b>", "col": 12}},
		{"id": "nur-nc0", "type": "number_card", "data": {"number_card_name": "Nursery Students", "col": 4}},
		{"id": "nur-nc1", "type": "number_card", "data": {"number_card_name": "Nursery Parents", "col": 4}},
		{"id": "nur-nc2", "type": "number_card", "data": {"number_card_name": "Nursery Attendance Records", "col": 4}},
		{"id": "nur-ch-h", "type": "header", "data": {"text": "<b>" + _("Charts") + "</b>", "col": 12}},
		{
			"id": "nur-ch0",
			"type": "chart",
			"data": {"chart_name": "Nursery Students by Status", "col": 6},
		},
		{
			"id": "nur-ch1",
			"type": "chart",
			"data": {"chart_name": "Nursery Attendance by Status", "col": 6},
		},
		{"id": "nur-rpt-h", "type": "header", "data": {"text": "<b>" + _("Reports") + "</b>", "col": 12}},
		{
			"id": "nur-rp0",
			"type": "shortcut",
			"data": {"shortcut_name": "Students by class", "col": 4},
		},
		{
			"id": "nur-rp1",
			"type": "shortcut",
			"data": {"shortcut_name": "Attendance summary", "col": 4},
		},
	]

	ws.content = json.dumps(blocks, ensure_ascii=False)
	ws.save(ignore_permissions=True)
