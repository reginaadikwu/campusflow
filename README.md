# CampusFlow

CampusFlow is a Python command-line helpdesk ticket management application. It creates and tracks support tickets, assigns staff, manages ticket status, saves data as JSON, and reports ticket totals.

## Requirements

- Python 3
- No third-party Python packages are required.

## Run the application

From the repository root:

```bash
python3 main.py
```

The application creates `data/tickets.json` when tickets are first saved.

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

## Ticket fields

Each ticket contains an ID, title, category, urgency, affected-user count, calculated priority, status, and assigned staff member.

Valid categories: Network, Hardware, Software, Other.

Valid urgency levels: low, medium, high.

## Priority rules

1. High urgency and at least 10 affected users: critical.
2. Otherwise, high urgency or at least 10 affected users: high.
3. Otherwise, medium urgency or at least 3 affected users: medium.
4. Otherwise: low.

## Workflow

New tickets start as open. A ticket must be assigned before moving to in_progress. A ticket can then be resolved. Resolved tickets must be explicitly reopened before further modification.

## Persistence

Tickets are stored in JSON. A missing data file is treated as an empty collection. Malformed JSON and invalid saved records produce errors instead of being silently accepted.

## Project structure

- `main.py`: command-line interface.
- `campusflow/tickets.py`: ticket creation, validation, and priority.
- `campusflow/workflow.py`: assignment and status transitions.
- `campusflow/storage.py`: JSON persistence.
- `campusflow/reports.py`: report generation.
- `tests/`: automated tests.
- `docs/`: design decisions and AI learning log.

## Current limitations

CampusFlow is a local command-line application. It does not provide a web interface, user authentication, or concurrent multi-user storage.
