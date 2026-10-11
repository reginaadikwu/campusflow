STATUS_ORDER = ("open", "in_progress", "resolved")
PRIORITY_ORDER = ("critical", "high", "medium", "low")


def generate_report(tickets):
    """Return total ticket count and counts by status and priority."""
    by_status = {status: 0 for status in STATUS_ORDER}
    by_priority = {priority: 0 for priority in PRIORITY_ORDER}

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]

        if status not in by_status:
            raise ValueError(f"Unknown ticket status: {status!r}")

        if priority not in by_priority:
            raise ValueError(f"Unknown ticket priority: {priority!r}")

        by_status[status] += 1
        by_priority[priority] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }

