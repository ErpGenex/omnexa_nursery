# omnexa_nursery

Integrated nursery management for **ErpGenEx** / **Frappe**: students, parents/guardians, educational activities, attendance, daily observations, transport routes, and fee structures — designed to integrate with **`omnexa_accounting`** (Sales Invoice, Payment Entry, Journal Entry).

## Requirements

- Frappe v15+
- `omnexa_core`
- `omnexa_accounting`

## Install

1. Add `omnexa_nursery` to `sites/apps.txt` (or clone into `apps/`).
2. From bench root:

```bash
./env/bin/pip install -e apps/omnexa_nursery
bench --site <yoursite> install-app omnexa_nursery
bench --site <yoursite> migrate
bench clear-cache
```

3. Open **Nursery Settings** (Single), choose **Company**, fill nursery profile, add enabled programs.

## Roadmap (not all implemented in v0.1)

- Automated monthly invoicing against fee structures and enrollments.
- Late payment notifications (Email/SMS/WhatsApp via platform configuration).
- Parent portal and advanced reporting.

See `Docs/2026-05-04/` for Arabic planning documents.

## License

MIT — see `license.txt`.
