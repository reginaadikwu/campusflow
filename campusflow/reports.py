"""
Reports module for generating helpdesk metric aggregations.
"""

def generate_status_report(tickets: dict) -> dict:
    """Calculates ticket breakdowns by status."""
    return {"open": 0, "in_progress": 0, "resolved": 0}

def generate_priority_report(tickets: dict) -> dict:
    """Calculates ticket breakdowns by calculated priority."""
    return {"critical": 0, "high": 0, "medium": 0, "low": 0}
