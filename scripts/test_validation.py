"""Guard the public data boundary against common editing mistakes."""
import copy
import json
import unittest
from validate import ROOT, validate

class PublicDataTest(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / "data/trip.json").read_text(encoding="utf-8"))

    def test_current_data_is_valid(self):
        validate(self.data)

    def test_private_fields_are_rejected(self):
        self.data["flights"] = []
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_personal_email_is_rejected_in_notes(self):
        self.data["days"][0]["note"] = "Contact traveler@example.com"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_absolute_travel_dates_are_rejected(self):
        self.data["days"][0]["note"] = "Depart 2030-01-02"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_google_collection_is_rejected(self):
        self.data["places"][0]["note"] = "https://maps.app.goo.gl/example"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_booking_parameters_are_rejected(self):
        self.data["resources"][0]["url"] += "?booking=example"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_only_aliases_are_allowed(self):
        self.data["checklist"][0]["owners"] = ["Traveler Real Name"]
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_private_lodging_map_is_rejected(self):
        self.data["places"][0]["mapQuery"] = "Example Hotel Honolulu"
        with self.assertRaises(ValueError):
            validate(self.data)

if __name__ == "__main__":
    unittest.main()
