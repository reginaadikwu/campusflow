
import re


VALID_CATEGORIES = {
    "network": "Network",
    "hardware": "Hardware",
    "software": "Software",
    "other": "Other",
}

VALID_URGENCIES = {"low", "medium", "high"}


def calculate_priority(urgency, affected_users):
    """Calculate ticket priority using the agreed rules."""
    if urgency not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")

    if (
        isinstance(affected_users, bool)
        or not isinstance(affected_users, int)
        or affected_users <= 0
    ):
        raise ValueError("Affected users must be a positive integer.")

    if urgency == "high" and affected_users >= 10:
        return "critical"

    if urgency == "high" or affected_users >= 10:
        return "high"

    if urgency == "medium" or affected_users >= 3:
        return "medium"

    return "low"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate and append a new ticket, then return it."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Ticket title must not be blank.")

    if not isinstance(category, str):
        raise ValueError("Category must be Network, Hardware, Software, or Other.")

    normalized_category = VALID_CATEGORIES.get(category.strip().lower())
    if normalized_category is None:
        raise ValueError("Category must be Network, Hardware, Software, or Other.")

    if not isinstance(urgency, str):
        raise ValueError("Urgency must be low, medium, or high.")

    normalized_urgency = urgency.strip().lower()
    if normalized_urgency not in VALID_URGENCIES:
        raise ValueError("Urgency must be low, medium, or high.")

    # Validate before changing the ticket collection.
    priority = calculate_priority(normalized_urgency, affected_users)

    # Find the highest existing numeric ticket ID.
    highest_id = 0
    existing_ids = set()

    for ticket in tickets:
        ticket_id = ticket.get("id")

        if ticket_id in existing_ids:
            raise ValueError(f"Duplicate ticket ID found: {ticket_id}")

        existing_ids.add(ticket_id)

        if isinstance(ticket_id, str):
            match = re.fullmatch(r"T(\d+)", ticket_id)
            if match:
                highest_id = max(highest_id, int(match.group(1)))

    next_number = highest_id + 1
    new_id = f"T{next_number:03d}"

    # Avoid collisions, including with IDs that don't follow the usual sequence.
    while new_id in existing_ids:
        next_number += 1
        new_id = f"T{next_number:03d}"

    ticket = {
        "id": new_id,
        "title": title.strip(),
        "category": normalized_category,
        "urgency": normalized_urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
    }

    tickets.append(ticket)
    return ticket
