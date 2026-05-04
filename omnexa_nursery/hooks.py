app_name = "omnexa_nursery"
app_title = "ErpGenEx — Nursery"
app_publisher = "ErpGenEx"
app_description = "Integrated nursery management: students, parents, activities, attendance, and billing"
app_email = "dev@erpgenex.com"
app_license = "mit"
app_version = "0.1.0"

required_apps = ["omnexa_core", "omnexa_accounting"]

add_to_apps_screen = [
	{
		"name": "omnexa_nursery",
		"logo": "/assets/omnexa_nursery/images/nursery.svg",
		"title": "Nursery",
		"route": "/app/nursery",
	}
]

app_include_css = "/assets/omnexa_nursery/css/nursery_desk.css"

before_install = "omnexa_nursery.install.before_install"
after_install = "omnexa_nursery.install.after_install"
before_migrate = "omnexa_nursery.install.before_migrate"

scheduler_events = {
	"monthly": [
		"omnexa_nursery.tasks.monthly_billing.run_monthly_billing",
	],
	"daily": [
		"omnexa_nursery.tasks.late_payment_alerts.run_late_payment_alerts",
	],
}
