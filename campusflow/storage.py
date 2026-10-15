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

LEGACY_FIELDS = REQUIRED_FIELDS
CURRENT_FIELDS = REQUIRED_FIELDS | {"notes"}

VALID_STATUSES = {"open", "in_progress", "resolved"}


def _validate_notes(ticket_id, notes):
    if not isinstance(notes, list):
        raise ValueError(f"{ticket_id}: notes must be a list.")

    seen_note_ids = set()

    for note in notes:
        if not isinstance(note, dict):
            raise ValueError(f"{ticket_id}: each note must be a dictionary.")

        if set(note) != {"note_id", "author", "message"}:
            raise ValueError(f"{ticket_id}: invalid note fields.")

        note_id = note["note_id"]
        if not isinstance(note_id, str) or not re.fullmatch(
            r"N\d{3,}", note_id
        ):
            raise ValueError(f"{ticket_id}: invalid note ID.")

        if note_id in seen_note_ids:
            raise ValueError(f"{ticket_id}: duplicate note ID {note_id}.")

        seen_note_ids.add(note_id)

        author = note["author"]
        if not isinstance(author, str) or not author.strip():
            raise ValueError(f"{ticket_id}: note author must not be blank.")

        message = note["message"]
        if (
            not isinstance(message, str)
            or not 5 <= len(message.strip()) <= 300
        ):
            raise ValueError(
                f"{ticket_id}: note message must contain 5 to 300 characters."
            )


def _validate_tickets(tickets):
    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")

    seen_ids = set()

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        fields = set(ticket)
        if fields != CURRENT_FIELDS:
            raise ValueError("Ticket contains missing or unexpected fields.")

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

        if ticket["category"] not in set(VALID_CATEGORIES.values()):
            raise ValueError(f"{ticket_id}: invalid category.")

        urgency = ticket["urgency"]
        if not isinstance(urgency, str) or urgency not in {
            "low", "medium", "high"
        }:
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

        if "notes" in ticket:
            _validate_notes(ticket_id, ticket["notes"])


def load_tickets(path):
    """Load and validate tickets, supporting legacy records without notes."""
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

    if not isinstance(tickets, list):
        raise ValueError("Ticket data must be a list.")

    # Work on copies so validation never partially changes loaded records.
    normalized = []
    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Each ticket must be a dictionary.")

        record = dict(ticket)
        if set(record) == LEGACY_FIELDS:
            record["notes"] = []
        elif set(record) != CURRENT_FIELDS:
            raise ValueError("Ticket contains missing or unexpected fields.")

        normalized.append(record)

    _validate_tickets(normalized)
    return normalized


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
