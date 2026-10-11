
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
    """Return unresolved tickets in priority and numeric-ID order."""
    unresolved = [
        ticket for ticket in tickets
        if ticket["status"] != "resolved"
    ]

    def sort_key(ticket):
        ticket_id = ticket["id"]
        return (
            PRIORITY_ORDER[ticket["priority"]],
            int(ticket_id[1:]),
        )

    return sorted(unresolved, key=sort_key)
