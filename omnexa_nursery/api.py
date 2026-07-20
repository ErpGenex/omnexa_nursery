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


@frappe.whitelist(allow_guest=True)
def get_site_config() -> dict:
	"""Public nursery website configuration."""
	return {
		"brand_name_ar": "Omnexa Nursery",
		"brand_name_en": "Omnexa Nursery",
		"tagline_ar": "رعاية تعليمية آمنة ومحبة لأطفالكم",
		"tagline_en": "Safe, loving educational care for your children",
		"hero_text_ar": "من الرعاية المبكرة إلى ما قبل المدرسة — بيئة آمنة ومحبة لنمو طفلك",
		"hero_text_en": "From infant care to preschool — a safe, loving environment for your child's growth",
		"hero_image": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?auto=format&fit=crop&w=1920&q=85",
		"logo": "/assets/omnexa_nursery/logo.png",
		"primary_color": "#e91e63",
		"secondary_color": "#9c27b0",
		"accent_color": "#00bcd4",
		"gold_color": "#ffc107",
		"programs": [
			{"key": "infant", "name_ar": "حضانة الأطفال", "name_en": "Infant Care", "icon": "👶", "age": "0-2 years"
	},
			{"key": "toddler", "name_ar": "الروضة", "name_en": "Toddler Program", "icon": "🧸", "age": "2-4 years"
	},
			{"key": "preschool", "name_ar": "ما قبل المدرسة", "name_en": "Preschool", "icon": "🎨", "age": "4-6 years"
	},
			{"key": "after_school", "name_ar": "برنامج بعد المدرسة", "name_en": "After School", "icon": "📚", "age": "6-12 years"
	},
		],
		"features": [
			{"icon": "👩‍🏫", "ar": "معلمون مؤهلون", "en": "Qualified Teachers"
	},
			{"icon": "🍎", "ar": "وجبات صحية", "en": "Healthy Meals"
	},
			{"icon": "🔒", "ar": "أمان وحماية", "en": "Safe Environment"
	},
			{"icon": "🎮", "ar": "أنشطة تعليمية", "en": "Learning Activities"
	},
			{"icon": "📱", "ar": "تطبيق أولياء الأمور", "en": "Parent App"
	},
			{"icon": "🏥", "ar": "رعاية صحية", "en": "Healthcare Support"
	},
		],
		"stats": {"children": 500, "teachers": 50, "families": 300, "years": 10}
	}
