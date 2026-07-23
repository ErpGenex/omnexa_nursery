# Copyright (c) 2026, Omnexa
import frappe
from omnexa_nursery.install import _import_workspace_artifacts

def execute():
	_import_workspace_artifacts()
	if frappe.db.exists("Workspace", "Nursery"):
		from omnexa_nursery.workspace.nurs_workspace import sync_nurs_workspace_menu
		sync_nurs_workspace_menu(save=True, rebuild=True)
