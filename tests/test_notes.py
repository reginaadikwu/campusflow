
import unittest

from campusflow.tickets import create_ticket
from campusflow.workflow import (
    add_ticket_note,
    assign_ticket,
    change_status,
    reopen_ticket,
)


class TestTicketNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        create_ticket(
            self.tickets, "Wi-Fi issue", "Network", "high", 10
        )

    def test_add_note_generates_id_and_trims_input(self):
        note = add_ticket_note(
            self.tickets, "T001", " Alex ", "  Checked the router  "
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Alex")
        self.assertEqual(note["message"], "Checked the router")

    def test_note_ids_increase_per_ticket(self):
        first = add_ticket_note(
            self.tickets, "T001", "Alex", "Checked router"
        )
        second = add_ticket_note(
            self.tickets, "T001", "Sam", "Restarted router"
        )

        self.assertEqual(first["note_id"], "N001")
        self.assertEqual(second["note_id"], "N002")

    def test_rejects_blank_author_without_mutation(self):
        ticket = self.tickets[0]
        original = ticket.copy()

        with self.assertRaises(ValueError):
            add_ticket_note(self.tickets, "T001", "  ", "Checked router")

        self.assertEqual(ticket, original)

    def test_rejects_short_message_without_mutation(self):
        ticket = self.tickets[0]
        original = ticket.copy()

        with self.assertRaises(ValueError):
            add_ticket_note(self.tickets, "T001", "Alex", "No")

        self.assertEqual(ticket, original)

    def test_rejects_message_over_300_characters(self):
        with self.assertRaises(ValueError):
            add_ticket_note(self.tickets, "T001", "Alex", "x" * 301)

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_rejects_notes_on_resolved_ticket(self):
        assign_ticket(self.tickets, "T001", "Alex")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")

        with self.assertRaises(ValueError):
            add_ticket_note(
                self.tickets, "T001", "Alex", "Reviewed the solution"
            )

    def test_notes_survive_resolve_and_reopen(self):
        add_ticket_note(
            self.tickets, "T001", "Alex", "Checked the router"
        )
        assign_ticket(self.tickets, "T001", "Alex")
        change_status(self.tickets, "T001", "in_progress")
        change_status(self.tickets, "T001", "resolved")
        reopen_ticket(self.tickets, "T001")

        self.assertEqual(
            self.tickets[0]["notes"][0]["note_id"], "N001"
        )


if __name__ == "__main__":
    unittest.main()
