
import json
import os
import re
import tempfile
from pathlib import Path

from campusflow.tickets import calculate_priority, VALID_CATEGORIES


REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}

VALID_STATUSES = {"open", "in_progress", "resolved"}


def _validate_tickets(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")

    seen_ids = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        if set(ticket) != REQUIRED_FIELDS:
            raise ValueError(
                "Each ticket must contain exactly the eight required fields."
            )

        ticket_id = ticket["id"]
        if not isinstance(ticket_id, str) or not re.fullmatch(
            r"T\d{3,}", ticket_id
        ):
            raise ValueError("Ticket IDs must use the format T001, T002, etc.")

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID: {ticket_id}")
        seen_ids.add(ticket_id)

        if not isinstance(ticket["title"], str) or not ticket["title"].strip():
            raise ValueError(f"{ticket_id}: title must not be blank.")

        category = ticket["category"]
        if category not in set(VALID_CATEGORIES.values()):
            raise ValueError(f"{ticket_id}: invalid category.")

        urgency = ticket["urgency"]
        if urgency not in {"low", "medium", "high"}:
            raise ValueError(f"{ticket_id}: invalid urgency.")

        expected_priority = calculate_priority(
            urgency, ticket["affected_users"]
        )
        if ticket["priority"] != expected_priority:
            raise ValueError(f"{ticket_id}: priority does not match its inputs.")

        if ticket["status"] not in VALID_STATUSES:
            raise ValueError(f"{ticket_id}: invalid status.")

        assigned_to = ticket["assigned_to"]
        if assigned_to is not None and (
            not isinstance(assigned_to, str) or not assigned_to.strip()
        ):
            raise ValueError(f"{ticket_id}: invalid assigned_to value.")


def load_tickets(path):
    """Load and validate tickets from JSON."""
    path = Path(path)

    try:
        with path.open("r", encoding="utf-8") as file:
            tickets = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Cannot load malformed JSON from {path}: {exc}"
        ) from exc
    except OSError as exc:
        raise OSError(f"Cannot read ticket file {path}: {exc}") from exc

    _validate_tickets(tickets)
    return tickets


def save_tickets(tickets, path):
    """Validate and atomically save tickets to JSON."""
    _validate_tickets(tickets)
    path = Path(path)

    temporary_path = None

    try:
        path.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as file:
            temporary_path = Path(file.name)
            json.dump(tickets, file, indent=2)
            file.write("\n")
            file.flush()
            os.fsync(file.fileno())

        os.replace(temporary_path, path)
        temporary_path = None

    except OSError as exc:
        raise OSError(f"Cannot save ticket file {path}: {exc}") from exc

    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

