# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

import frappe

from omnexa_nursery.utils.monthly_billing import generate_monthly_invoices


@frappe.whitelist()
def run_monthly_billing_now():
	"""Run the same job as the monthly scheduler (manually from Desk / API)."""
	frappe.only_for(("System Manager", "Nursery Administrator", "Nursery Accountant"))
	return generate_monthly_invoices()
