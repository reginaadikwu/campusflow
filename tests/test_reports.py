import unittest

from campusflow.reports import generate_report
from campusflow.tickets import create_ticket
from campusflow.workflow import assign_ticket, change_status


class TestReports(unittest.TestCase):
    def setUp(self):
        self.tickets = []

        create_ticket(self.tickets, "Network outage", "Network", "high", 10)
        create_ticket(self.tickets, "Printer issue", "Hardware", "low", 1)
        create_ticket(self.tickets, "Application error", "Software", "medium", 3)

    def test_empty_report(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(sum(report["by_status"].values()), 0)
        self.assertEqual(sum(report["by_priority"].values()), 0)

    def test_report_counts_statuses_and_priorities(self):
        assign_ticket(self.tickets, "T001", "Wisdom")
        change_status(self.tickets, "T001", "in_progress")

        report = generate_report(self.tickets)

        self.assertEqual(report["total"], 3)
        self.assertEqual(
            report["by_status"],
            {"open": 2, "in_progress": 1, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 1, "high": 0, "medium": 1, "low": 1},
        )

    def test_report_counts_resolved_tickets(self):
        assign_ticket(self.tickets, "T001", "Regina")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        report = generate_report(self.tickets)

        self.assertEqual(report["by_status"]["resolved"], 1)
        self.assertEqual(report["total"], 3)


if __name__ == "__main__":
    unittest.main()

