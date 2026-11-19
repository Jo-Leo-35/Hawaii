"""Guard the public data boundary against common editing mistakes."""
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

    def test_generic_map_search_is_rejected(self):
        self.data["places"][0]["mapUrl"] = "https://www.google.com/maps/search/?api=1&query=Musubi+Waikiki"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_unknown_stop_destination_is_rejected(self):
        self.data["days"][0]["stops"][0]["placeId"] = "missing-location"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_maps_account_parameters_are_rejected(self):
        self.data["places"][0]["mapUrl"] += "?authuser=0"
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_wrong_island_is_rejected(self):
        self.data["places"][0]["mapUrl"] = self.data["places"][0]["mapUrl"].replace("!3d21.", "!3d20.")
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_duplicate_place_ids_are_rejected(self):
        self.data["places"][1]["id"] = self.data["places"][0]["id"]
        with self.assertRaises(ValueError):
            validate(self.data)

    def test_public_hotels_are_allowed(self):
        validate(self.data)
        places = {p["id"]:p for p in self.data["places"]}
        self.assertEqual(self.data["days"][0]["lodging"], ["stay"])
        self.assertEqual(self.data["days"][2]["lodging"], ["stay", "hilton"])
        self.assertEqual(places["stay"]["address"], "2424 Koa Avenue, Honolulu, HI 96815")
        self.assertEqual(places["hilton"]["address"], "2330 Kuhio Avenue, Honolulu, HI 96815")

    def test_hotel_reference_must_be_lodging(self):
        self.data["days"][0]["lodging"] = ["gojump"]
        with self.assertRaises(ValueError):
            validate(self.data)

if __name__ == "__main__":
    unittest.main()
