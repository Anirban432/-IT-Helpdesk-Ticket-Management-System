# ServiceDesk — IT Help Desk & Incident Management Portal

A portfolio-ready IT service desk demo built with Python, Streamlit and SQLite. It demonstrates a simple incident lifecycle: request intake, categorisation, prioritisation, assignment, work notes, resolution tracking and reporting.

## Features

- Submit support tickets with requester details and issue descriptions
- Automatically generated ticket IDs (`HD-0001`, etc.)
- Categories for hardware, software, network, email/accounts and access issues
- Four priority levels and a ticket status workflow
- Search, filter, assign and update tickets
- Add internal troubleshooting notes and resolution details
- Dashboard metrics and charts
- CSV export for reporting
- SQLite persistence between application restarts

## Requirements

- Python 3.10 or newer
- pip

## Run locally (Windows)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit (normally `http://localhost:8501`).

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The SQLite database (`helpdesk.db`) is created automatically beside `app.py` on first launch. It is intentionally excluded from Git so each user starts with a clean local demo database.

## Suggested demo workflow

1. Open **Create ticket** and submit a sample Wi-Fi connectivity incident.
2. Open **Manage tickets**, assign it to a technician and change its status to **In Progress**.
3. Add a troubleshooting note describing checks such as adapter status, IP configuration and DNS resolution.
4. Add the resolution and set the status to **Resolved**.
5. Review the dashboard and download the CSV report.

Use fictional requester data in public demos. This project is a learning/portfolio application, not a production ITSM platform: it does not include authentication, role-based access control, email notifications, SLA timers or hardened deployment controls.

## Project structure

```text
it-helpdesk-system/
├── app.py              # Streamlit interface and application logic
├── requirements.txt    # Python dependencies
├── README.md           # Setup and usage guide
└── .gitignore          # Excludes local database and environment files
```

## Resume description (use after you have run and tested it)

**ServiceDesk — IT Help Desk & Incident Management Portal | Python, Streamlit, SQLite, Pandas**
- Built a web-based service desk application to log, categorise, prioritise and track IT incidents through resolution.
- Implemented persistent ticket storage, technician assignment, status updates and troubleshooting notes using SQLite.
- Developed an operational dashboard with incident metrics, category/priority breakdowns, search, filters and CSV reporting.

## Author

Anirban Banerjee
