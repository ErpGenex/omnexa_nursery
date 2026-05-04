# Copyright (c) 2026, ErpGenEx and contributors
# License: MIT. See license.txt

"""Generate monthly Sales Invoices for nursery fees (omnexa_accounting)."""

from __future__ import annotations

from datetime import date

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, get_first_day, getdate, today

from omnexa_nursery.utils.nursery_items import ensure_nursery_service_items


def _company_currency(company: str) -> str:
	cur = frappe.db.get_value("Company", company, "default_currency")
	if not cur:
		frappe.throw(_("Company {0} has no default currency.").format(company))
	return cur


def _default_branch(company: str, preferred: str | None) -> str | None:
	if preferred and frappe.db.exists("Branch", preferred):
		co = frappe.db.get_value("Branch", preferred, "company")
		if co == company:
			return preferred
	br = frappe.db.sql(
		"SELECT name FROM `tabBranch` WHERE company=%s ORDER BY creation ASC LIMIT 1",
		(company,),
	)
	return br[0][0] if br else None


def _default_income_account(company: str) -> str | None:
	for fld in ("default_service_revenue_gl", "default_sales_revenue_gl"):
		if frappe.get_meta("Company").has_field(fld):
			acc = frappe.db.get_value("Company", company, fld)
			if acc:
				return acc
	return None


def _match_fee_structure(company: str, class_room: str | None):
	if not class_room:
		return None
	target = (class_room or "").strip().lower()
	rows = frappe.get_all(
		"Nursery Fee Structure",
		filters={"company": company},
		fields=["name", "fee_class"],
	)
	for row in rows:
		if (row.fee_class or "").strip().lower() == target:
			return frappe.get_doc("Nursery Fee Structure", row.name)
	return None


def _billing_reference(company: str, period: str, parent_profile: str) -> str:
	return f"Nursery Monthly|{company}|{period}|{parent_profile}"


def _invoice_exists(company: str, reference: str) -> bool:
	name = frappe.db.sql(
		"""
		SELECT name FROM `tabSales Invoice`
		WHERE company=%s AND reference=%s AND docstatus < 2
		LIMIT 1
		""",
		(company, reference),
	)
	return bool(name)


def generate_monthly_invoices(
	*,
	posting_date: date | None = None,
	billing_year: int | None = None,
	billing_month: int | None = None,
) -> dict:
	"""Create one Sales Invoice per Nursery Parent Profile that has Customer (aggregate active students).

	If billing_year/month omitted, bills the **previous calendar month** relative to posting_date (or today).
	"""
	if not frappe.db.get_single_value("Nursery Settings", "setup_complete"):
		return {"ok": False, "skipped": True, "reason": "Nursery Settings not completed"}

	auto_bill = frappe.db.get_single_value("Nursery Settings", "auto_bill_enabled")
	if auto_bill is None:
		auto_bill = 1
	if not cint(auto_bill):
		return {"ok": False, "skipped": True, "reason": "auto_bill_enabled is off"}

	company = frappe.db.get_single_value("Nursery Settings", "company")
	if not company:
		return {"ok": False, "skipped": True, "reason": "No company on Nursery Settings"}

	pdate = getdate(posting_date or today())
	if billing_year is None or billing_month is None:
		first_this = get_first_day(pdate)
		last_prev = add_days(first_this, -1)
		billing_year = last_prev.year
		billing_month = last_prev.month

	period = f"{billing_year:04d}-{billing_month:02d}"
	posting = pdate

	items_map = ensure_nursery_service_items(company)
	income_account = _default_income_account(company)
	currency = _company_currency(company)
	pref_branch = frappe.db.get_single_value("Nursery Settings", "default_branch")
	branch = _default_branch(company, pref_branch)
	if not branch:
		return {"ok": False, "error": _("No Branch found for company {0}. Create a Branch first.").format(company)}

	tax_rule = frappe.db.get_single_value("Nursery Settings", "default_tax_rule")

	created = []
	skipped = []
	errors = []

	parents = frappe.get_all(
		"Nursery Parent Profile",
		filters={"company": company},
		pluck="name",
	)

	for parent in parents:
		try:
			customer = frappe.db.get_value("Nursery Parent Profile", parent, "customer")
			if not customer:
				skipped.append({"parent": parent, "reason": "no_customer"})
				continue

			ref = _billing_reference(company, period, parent)
			if _invoice_exists(company, ref):
				skipped.append({"parent": parent, "reason": "already_billed", "reference": ref})
				continue

			students = frappe.get_all(
				"Nursery Student",
				filters={"company": company, "primary_parent": parent, "status": "Active"},
				fields=["name", "class_room", "full_name_ar"],
			)
			if not students:
				skipped.append({"parent": parent, "reason": "no_active_students"})
				continue

			si = frappe.new_doc("Sales Invoice")
			si.company = company
			si.branch = branch
			si.customer = customer
			si.posting_date = posting
			si.currency = currency
			si.conversion_rate = 1.0
			si.reference = ref
			si.external_reference = period
			if tax_rule:
				si.default_tax_rule = tax_rule

			for st in students:
				fs = _match_fee_structure(company, st.class_room)
				st_label = st.full_name_ar or st.name

				if fs:
					if flt(fs.tuition_fee):
						si.append(
							"items",
							{
								"item": items_map["tuition"],
								"qty": 1,
								"rate": flt(fs.tuition_fee),
								"income_account": income_account,
								"external_reference": f"{st_label} — Tuition ({period})",
							},
						)
					if flt(fs.transport_fee):
						si.append(
							"items",
							{
								"item": items_map["transport"],
								"qty": 1,
								"rate": flt(fs.transport_fee),
								"income_account": income_account,
								"external_reference": f"{st_label} — Transport ({period})",
							},
						)
					if flt(fs.meal_fee):
						si.append(
							"items",
							{
								"item": items_map["meal"],
								"qty": 1,
								"rate": flt(fs.meal_fee),
								"income_account": income_account,
								"external_reference": f"{st_label} — Meals ({period})",
							},
						)

				enrolls = frappe.get_all(
					"Nursery Activity Enrollment",
					filters={
						"company": company,
						"student": st.name,
						"status": "Active",
					},
					fields=["name", "monthly_fee", "activity"],
				)
				if enrolls:
					for en in enrolls:
						rate = flt(en.monthly_fee)
						if not rate:
							act_fee = frappe.db.get_value("Nursery Educational Activity", en.activity, "monthly_fee")
							rate = flt(act_fee)
						if rate:
							act_label = (
								frappe.db.get_value("Nursery Educational Activity", en.activity, "activity_name") or en.activity
							)
							si.append(
								"items",
								{
									"item": items_map["activity"],
									"qty": 1,
									"rate": rate,
									"income_account": income_account,
									"external_reference": f"{st_label} — {act_label} ({period})",
								},
							)
				elif fs and flt(fs.activity_fee):
					si.append(
						"items",
						{
							"item": items_map["activity"],
							"qty": 1,
							"rate": flt(fs.activity_fee),
							"income_account": income_account,
							"external_reference": f"{st_label} — Activities bundle ({period})",
						},
					)

			if not si.items:
				skipped.append({"parent": parent, "reason": "no_fee_lines"})
				continue

			due_days = cint(frappe.db.get_single_value("Nursery Settings", "invoice_due_days") or 0)
			if due_days:
				si.due_date = add_days(si.posting_date, due_days)

			si.insert(ignore_permissions=True)
			si.submit()
			created.append(si.name)
		except Exception:
			errors.append({"parent": parent, "error": frappe.get_traceback(with_context=True)})
			frappe.log_error(frappe.get_traceback(), f"Nursery billing failed for {parent}")

	return {
		"ok": True,
		"period": period,
		"posting_date": str(posting),
		"created": created,
		"skipped": skipped,
		"errors": errors,
	}
