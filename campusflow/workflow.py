
PRIORITY_ORDER = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
}


def _find_ticket(tickets, ticket_id):
    """Return a ticket or raise KeyError if it doesn't exist."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise KeyError(f"Ticket {ticket_id!r} was not found.")


def _ensure_not_resolved(ticket):
    """Prevent modifications to resolved tickets."""
    if ticket["status"] == "resolved":
        raise ValueError(
            "This ticket is resolved. Reopen it before modifying it."
        )


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket without changing its status."""
    ticket = _find_ticket(tickets, ticket_id)
    _ensure_not_resolved(ticket)

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name must not be blank.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def change_status(tickets, ticket_id, new_status):
    """Move a ticket through the supported workflow."""
    ticket = _find_ticket(tickets, ticket_id)
    _ensure_not_resolved(ticket)

    if not isinstance(new_status, str):
        raise ValueError("Status must be in_progress or resolved.")

    new_status = new_status.strip().lower()

    if new_status not in {"in_progress", "resolved"}:
        raise ValueError(
            "Use in_progress or resolved. Use reopen_ticket() to reopen a ticket."
        )

    current_status = ticket["status"]

    if current_status == "open" and new_status == "in_progress":
        if ticket["assigned_to"] is None:
            raise ValueError("Assign the ticket before starting work.")

    elif current_status == "in_progress" and new_status == "resolved":
        pass

    else:
        raise ValueError(
            f"Invalid status transition: {current_status} -> {new_status}."
        )

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    return ticket



def get_work_queue(tickets):
    """Return only open tickets, sorted by priority and numeric ticket ID."""
    open_tickets = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    def sort_key(ticket):
        ticket_id = ticket["id"]
        return (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket_id[1:]),
        )

    return sorted(open_tickets, key=sort_key)


def add_ticket_note(tickets, ticket_id, author, message):
    """Add a validated note to an open or in-progress ticket."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] not in {"open", "in_progress"}:
        raise ValueError("Notes can only be added to open or in-progress tickets.")

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Author must not be blank.")

    if not isinstance(message, str):
        raise ValueError("Note message must be text.")

    author = author.strip()
    message = message.strip()

    if not 5 <= len(message) <= 300:
        raise ValueError("Note message must contain 5 to 300 characters.")

    existing_notes = ticket.get("notes", [])

    if not isinstance(existing_notes, list):
        raise ValueError("Ticket notes must be a list.")

    used_ids = set()
    highest_number = 0

    for note in existing_notes:
        if not isinstance(note, dict):
            raise ValueError("Each note must be a dictionary.")

        note_id = note.get("note_id")

        if not isinstance(note_id, str):
            raise ValueError("Each note must have a valid note ID.")

        if note_id in used_ids:
            raise ValueError(f"Duplicate note ID: {note_id}")

        used_ids.add(note_id)

        if note_id.startswith("N") and note_id[1:].isdigit():
            highest_number = max(highest_number, int(note_id[1:]))

    next_number = highest_number + 1
    note_id = f"N{next_number:03d}"

    while note_id in used_ids:
        next_number += 1
        note_id = f"N{next_number:03d}"

    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    # Change the ticket only after validation succeeds.
    updated_notes = list(existing_notes)
    updated_notes.append(note)
    ticket["notes"] = updated_notes

    return note
