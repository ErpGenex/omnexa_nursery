# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

"""Late payment reminders — skeleton (Email/SMS/WhatsApp via platform integrations)."""

import frappe


def run_late_payment_alerts():
	if not frappe.db.get_single_value("Nursery Settings", "setup_complete"):
		return
	# TODO: query overdue invoices / balances and enqueue notifications
	frappe.logger("omnexa_nursery").info("run_late_payment_alerts: stub executed")
