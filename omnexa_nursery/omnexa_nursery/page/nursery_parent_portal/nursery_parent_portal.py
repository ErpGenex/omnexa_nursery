# Copyright (c) 2026, Omnexa and contributors
# License: MIT

"""Nursery Parent Portal Page."""

import frappe
from frappe import _
from frappe.utils import nowdate


def get_context(context):
    context.no_cache = 1
    context.user = frappe.session.user
    parent = get_parent_info(context.user)
    context.parent = parent
    context.stats = get_portal_statistics(parent)
    context.children = get_parent_children(parent)
    context.enrollments = get_parent_enrollments(parent)
    context.invoices = get_parent_invoices(parent)
    return context


def get_parent_info(user):
    parent = frappe.db.get_value("Guardian", {"email_id": user}, ["name", "guardian_name", "phone", "address"])
    if not parent:
        return None
    return {"name": parent[0], "guardian_name": parent[1], "phone": parent[2], "address": parent[3]}


def get_portal_statistics(parent):
    if not parent:
        return {}
    return {
        "total_children": frappe.db.count("Student", {"guardian": parent["name"], "disabled": 0}),
        "active_enrollments": frappe.db.count("Student Enrollment", {"guardian": parent["name"], "status": "Active"}),
        "completed_enrollments": frappe.db.count("Student Enrollment", {"guardian": parent["name"], "status": "Completed"}),
        "total_invoices": frappe.db.count("Sales Invoice", {"customer": parent["name"], "docstatus": 1}),
        "pending_invoices": frappe.db.count("Sales Invoice", {"customer": parent["name"], "status": "Overdue"}),
    }


def get_parent_children(parent, limit=10):
    if not parent:
        return []
    return frappe.get_all("Student", filters={"guardian": parent["name"], "disabled": 0}, fields=["name", "student_name", "date_of_birth", "gender", "student_group"], order_by="student_name", limit=limit)


def get_parent_enrollments(parent, limit=10):
    if not parent:
        return []
    return frappe.get_all("Student Enrollment", filters={"guardian": parent["name"], "docstatus": ["<", 2]}, fields=["name", "student", "academic_year", "program", "enrollment_date", "status"], order_by="enrollment_date desc", limit=limit)


def get_parent_invoices(parent, limit=10):
    if not parent:
        return []
    return frappe.get_all("Sales Invoice", filters={"customer": parent["name"], "docstatus": 1}, fields=["name", "posting_date", "grand_total", "outstanding_amount", "status"], order_by="posting_date desc", limit=limit)


@frappe.whitelist()
def create_enrollment(student, academic_year, program):
    try:
        parent = get_parent_info(frappe.session.user)
        if not parent:
            return {"success": False, "message": _("Parent not found")}
        enrollment = frappe.new_doc("Student Enrollment")
        enrollment.student = student
        enrollment.guardian = parent["name"]
        enrollment.academic_year = academic_year
        enrollment.program = program
        enrollment.enrollment_date = nowdate()
        enrollment.status = "Active"
        enrollment.save()
        enrollment.submit()
        return {"success": True, "enrollment": enrollment.name}
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_student_details(student_name):
    try:
        student = frappe.get_doc("Student", student_name)
        return {
            "success": True,
            "student_name": getattr(student, "student_name", None),
            "date_of_birth": getattr(student, "date_of_birth", None),
            "gender": getattr(student, "gender", None),
            "student_group": getattr(student, "student_group", None),
            "guardian": getattr(student, "guardian", None),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


@frappe.whitelist()
def get_student_attendance(student_name, from_date, to_date):
    try:
        attendance = frappe.get_all(
            "Student Attendance",
            filters={"student": student_name, "date": ["between", [from_date, to_date]]},
            fields=["date", "status", "leave_reason"],
            order_by="date",
        )
        return {"success": True, "attendance": attendance}
    except Exception as e:
        return {"success": False, "message": str(e)}
