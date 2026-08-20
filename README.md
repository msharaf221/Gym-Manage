# 💪 Power Home Gym Management System

A complete web-based gym management solution — members, subscriptions, attendance,
finance, staff payroll, and automated WhatsApp communications — built with **Flask + SQLite**.

## Quick Start

```bash
cd powerhome-gym
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:5000` and sign in with the default admin:

| Username | Password |
|----------|----------|
| `admin`  | `admin123` |

> **Change the admin password immediately after first login.**

## Project Structure

```
powerhome-gym/
├── app.py                 # Flask app + all routes & business logic
├── db.py                  # SQLite schema + connection helpers
├── utils.py               # Business-day logic, barcode/QR, WhatsApp, audit
├── requirements.txt
├── templates/             # Jinja2 templates (Bootstrap 5)
└── static/
    ├── barcodes/          # Generated Code128 barcodes + QR codes
    └── uploads/           # Member/product photos
```

## Features

- **Members** — profile photo, gender, Arabic-name barcode (Code128) + QR code, search by name/phone/WhatsApp/ID
- **Subscriptions** — plans: `month`, `month_cardio`, `15days`, `half_cardio`, `quarter`, `half_year`, `year`
- **Check-in** — barcode/QR scan or manual search, expiry validation, WhatsApp alert
- **Finance** — unified `cash_flow` ledger, multi-currency, cash & wallet payment methods
- **Products & Sales** — inventory with stock tracking, auto-deduct on sale
- **Daily Sessions** — drop-in classes with per-session payments & usage tracking
- **Withdrawals** — expense logging
- **Staff & Salaries** — employees, loans/advances, payroll (net = salary − advances), soft-delete archive
- **Reports** — daily breakdown, last-6-months comparison, monthly snapshots, Excel export (members + financial)
- **Users & Permissions** — role-based (admin vs staff) with granular permission flags
- **Audit Log** — full activity tracking
- **Notifications** — in-app, real-time
- **WhatsApp** — Cloud API (primary) with pywhatkit fallback, message templates, bulk reminders

## Business Logic

- **Business Day** — rolls over at a configurable hour (default **4 AM**)
- **Business Month** — starts on a configurable day (default **25th**)
- All financial reports follow this logic automatically.

## WhatsApp Setup

1. Go to **Settings → WhatsApp Integration**
2. Enable WhatsApp and paste your **Cloud API Token** + **Phone Number ID**
3. Customize templates (welcome, renewal reminder, debt alert, freeze/unfreeze)

If Cloud API is not configured, the system falls back to `pywhatkit`
(install it separately — it requires a logged-in WhatsApp Web session).

## Deployment

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Backup the database:

```bash
cp gym.db gym_backup_$(date +%Y%m%d).db
```

## License

Proprietary — all rights reserved.
