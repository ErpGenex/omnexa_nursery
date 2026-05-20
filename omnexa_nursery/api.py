# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe

from omnexa_nursery.utils.monthly_billing import generate_monthly_invoices


@frappe.whitelist()
def run_monthly_billing_now():
	"""Run the same job as the monthly scheduler (manually from Desk / API)."""
	frappe.only_for(("System Manager", "Nursery Administrator", "Nursery Accountant"))
	return generate_monthly_invoices()

@frappe.whitelist()
def preview_sector_kpi(scenario: str | None = None, params: str | None = None) -> dict:
	"""SAP Wave C — sector KPI preview (omnexa_core bridge)."""
	from omnexa_core.omnexa_core.vertical_api import preview_sector_kpi as _core_preview

	return _core_preview("nursery", scenario=scenario, params=params)

