import json
import tempfile
import unittest
from pathlib import Path

from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "tickets.json"
        self.tickets = []
        create_ticket(
            self.tickets, "Network outage", "Network", "high", 10
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_load_round_trip(self):
        save_tickets(self.tickets, self.path)
        loaded = load_tickets(self.path)

        self.assertEqual(loaded, self.tickets)

    def test_legacy_ticket_loads_with_empty_notes(self):
        legacy_ticket = {
            key: value
            for key, value in self.tickets[0].items()
            if key != "notes"
        }
        self.path.write_text(
            json.dumps([legacy_ticket]),
            encoding="utf-8",
        )

        loaded = load_tickets(self.path)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]["id"], legacy_ticket["id"])
        self.assertEqual(loaded[0]["notes"], [])

    def test_malformed_json_raises_error(self):
        self.path.write_text("{not valid json", encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "{not valid json",
        )

    def test_non_list_json_is_rejected(self):
        self.path.write_text('{"ticket": "T001"}', encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_record_is_rejected(self):
        invalid = [self.tickets[0].copy()]
        invalid[0]["affected_users"] = True

        self.path.write_text(json.dumps(invalid), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_duplicate_ids_are_rejected(self):
        duplicate = [
            self.tickets[0].copy(),
            self.tickets[0].copy(),
        ]
        self.path.write_text(json.dumps(duplicate), encoding="utf-8")

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_invalid_save_does_not_replace_existing_file(self):
        self.path.write_text("existing content", encoding="utf-8")

        invalid = [self.tickets[0].copy()]
        invalid[0]["priority"] = "low"

        with self.assertRaises(ValueError):
            save_tickets(invalid, self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            "existing content",
        )


if __name__ == "__main__":
    unittest.main()

