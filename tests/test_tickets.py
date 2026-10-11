
import unittest

from campusflow.tickets import calculate_priority, create_ticket


class TestCalculatePriority(unittest.TestCase):
    def test_critical_priority(self):
        self.assertEqual(calculate_priority("high", 10), "critical")

    def test_high_priority_from_urgency(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_high_priority_from_affected_users(self):
        self.assertEqual(calculate_priority("low", 10), "high")

    def test_medium_priority(self):
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")

    def test_low_priority(self):
        self.assertEqual(calculate_priority("low", 2), "low")

    def test_rejects_invalid_urgency(self):
        with self.assertRaises(ValueError):
            calculate_priority("urgent", 2)

    def test_rejects_invalid_affected_users(self):
        for value in (0, -1, 1.5, "3", True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    calculate_priority("low", value)


class TestCreateTicket(unittest.TestCase):
    def setUp(self):
        self.tickets = []

    def test_creates_ticket_with_required_fields(self):
        ticket = create_ticket(
            self.tickets, "Wi-Fi is down", "network", "HIGH", 10
        )

        self.assertEqual(
            set(ticket),
            {
                "id", "title", "category", "urgency",
                "affected_users", "priority", "status", "assigned_to",
            },
        )
        self.assertEqual(ticket["id"], "T001")
        self.assertEqual(ticket["category"], "Network")
        self.assertEqual(ticket["urgency"], "high")
        self.assertEqual(ticket["priority"], "critical")
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])
        self.assertEqual(len(self.tickets), 1)

    def test_generates_next_id(self):
        create_ticket(self.tickets, "First", "Other", "low", 1)
        ticket = create_ticket(self.tickets, "Second", "Other", "low", 1)

        self.assertEqual(ticket["id"], "T002")

    def test_rejects_blank_title_without_mutation(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "   ", "Other", "low", 1)

        self.assertEqual(self.tickets, [])

    def test_rejects_invalid_category_without_mutation(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Printer issue", "Furniture", "low", 1)

        self.assertEqual(self.tickets, [])

    def test_rejects_invalid_user_count_without_mutation(self):
        with self.assertRaises(ValueError):
            create_ticket(self.tickets, "Printer issue", "Other", "low", True)

        self.assertEqual(self.tickets, [])


if __name__ == "__main__":
    unittest.main()
