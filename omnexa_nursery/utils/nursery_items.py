# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

"""Ensure service Items exist for nursery billing lines (omnexa_accounting Sales Invoice)."""

from __future__ import annotations

import frappe
from frappe.utils import cstr


def _first_uom() -> str:
	uom = frappe.db.sql("SELECT name FROM `tabUOM` ORDER BY name ASC LIMIT 1", as_list=True)
	return uom[0][0] if uom else "Unit"


def _abbr(company: str) -> str:
	a = frappe.db.get_value("Company", company, "abbr") if company else None
	return cstr(a or company or "CO").strip().replace(" ", "")[:10]


def ensure_nursery_service_items(company: str) -> dict[str, str]:
	"""Return map keys tuition|transport|meal|activity -> Item name."""
	if not company:
		frappe.throw("Company is required")
	uom = _first_uom()
	abbr = _abbr(company)
	specs = (
		("tuition", f"NS-TU-{abbr}", "Nursery Tuition Fee"),
		("transport", f"NS-TR-{abbr}", "Nursery Transport Fee"),
		("meal", f"NS-ML-{abbr}", "Nursery Meal Fee"),
		("activity", f"NS-AC-{abbr}", "Nursery Activity Fee"),
	)
	out: dict[str, str] = {}
	for key, code, title in specs:
		name = frappe.db.get_value("Item", {"item_code": code, "company": company}, "name")
		if name:
			out[key] = name
			continue
		doc = frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": code,
				"item_name": title,
				"product_type": "Service",
				"company": company,
				"stock_uom": uom,
				"is_stock_item": 0,
				"is_sales_item": 1,
				"is_purchase_item": 0,
			}
		)
		doc.insert(ignore_permissions=True)
		out[key] = doc.name
	return out
