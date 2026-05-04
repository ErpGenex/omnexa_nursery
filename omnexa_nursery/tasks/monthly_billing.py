# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

"""Monthly billing scheduler — creates Sales Invoices via omnexa_accounting."""

import json

import frappe

from omnexa_nursery.utils.monthly_billing import generate_monthly_invoices


def run_monthly_billing():
	out = generate_monthly_invoices()
	frappe.logger("omnexa_nursery").info("run_monthly_billing: " + json.dumps(out, default=str)[:2000])
	return out
