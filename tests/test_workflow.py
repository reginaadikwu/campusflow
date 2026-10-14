
import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    assign_ticket,
    change_status,
    get_work_queue,
    reopen_ticket,
)


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Network outage", "Network", "high", 10)
        create_ticket(self.tickets, "Printer issue", "Hardware", "low", 1)
        create_ticket(self.tickets, "App error", "Software", "medium", 3)

    def test_assignment_does_not_change_status(self):
        ticket = assign_ticket(self.tickets, "T001", "Wisdom")

        self.assertEqual(ticket["assigned_to"], "Wisdom")
        self.assertEqual(ticket["status"], "open")

    def test_cannot_start_unassigned_ticket(self):
        before = self.tickets[0].copy()

        with self.assertRaises(ValueError):
            change_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0], before)

    def test_valid_status_transitions(self):
        assign_ticket(self.tickets, "T001", "Regina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_resolved_ticket_must_be_reopened_before_assignment(self):
        assign_ticket(self.tickets, "T001", "Regina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        before = self.tickets[0].copy()

        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T001", "Wisdom")

        self.assertEqual(self.tickets[0], before)

    def test_reopen_resolved_ticket(self):
        assign_ticket(self.tickets, "T001", "Regina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")

    def test_rejects_unknown_ticket(self):
        with self.assertRaises(KeyError):
            assign_ticket(self.tickets, "T999", "Regina")

    def test_queue_excludes_resolved_tickets(self):
        assign_ticket(self.tickets, "T001", "Regina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        queue = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T003", "T002"],
        )

   
    def test_queue_sorts_by_priority_then_numeric_id(self):
        queue = get_work_queue(self.tickets)

        self.assertEqual(
            [ticket["id"] for ticket in queue],
            ["T001", "T003", "T002"],
        )

    
    def test_queue_excludes_in_progress_tickets(self):
        tickets = [
            {
                "id": "T001",
                "title": "Wi-Fi issue",
                "category": "Network",
                "urgency": "high",
                "affected_users": 10,
                "priority": "critical",
                "status": "in_progress",
                "assigned_to": "Alex",
            },
            {
                "id": "T002",
                "title": "Laptop issue",
                "category": "Hardware",
                "urgency": "low",
                "affected_users": 1,
                "priority": "low",
                "status": "open",
                "assigned_to": None,
            },
        ]

        queue = get_work_queue(tickets)

        self.assertEqual([ticket["id"] for ticket in queue], ["T002"])


if __name__ == "__main__":
    unittest.main()
