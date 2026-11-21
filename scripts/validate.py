"""Validate the editable public itinerary before publication (standard library only)."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"planned", "pending", "confirmed", "optional"}
OWNERS = {"Leo", "Tyson"}
PUBLIC_IMAGES = {'./assets/places/toriton.jpg', './assets/places/sweet.jpg', './assets/places/patagonia.jpg', './assets/places/lulus.jpg', './assets/places/coffee.jpg', './assets/places/rainbow.jpg', './assets/places/market.png', './assets/places/dukes.jpg', './assets/kualoa-ranch.jpg', './assets/places/kaimana.jpg', './assets/places/dolphins.webp', './assets/hanauma-bay.jpg', './assets/places/ray.jpg', './assets/places/tamafuji.jpg', './assets/places/stay.jpg', './assets/places/ihop.jpg', './assets/waikiki.jpg', './assets/places/hilton.jpg', './assets/places/kualoa.jpg', './assets/places/ala.jpg', './assets/places/ono.jpg', './assets/places/gio-north.jpg', './assets/places/jenny.jpg', './assets/places/gio-city.jpg', './assets/places/asahi.jpg', './assets/places/ice.jpg', './assets/places/garden.jpg', './assets/places/gojump.webp', './assets/places/hanauma.jpg', './assets/hero-oahu.webp', './assets/places/musubi.jpg', './assets/places/maguro.jpg', './assets/places/leonards.jpg'}
ALLOWED_HOSTS = {
    "gojump-hawaii.com", "www.honolulu.gov", "www.kualoa.com",
    "funergygroup.com", "dolphinsandyou.com", "www.avis.com",
    "www.tablecheck.com", "esta.cbp.dhs.gov", "www.enterprise.com",
}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def fields(value, required, optional=()):
    require(isinstance(value, dict), "Expected an object")
    require(set(required) <= set(value), "Missing required fields")
    require(set(value) <= set(required) | set(optional), "Unexpected fields; keep private records outside this file")

def text(value):
    require(isinstance(value, str) and 0 < len(value) <= 1200, "Expected non-empty text")

def url(value):
    text(value)
    parsed = urlparse(value)
    require(parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS, "Resource must use an approved official HTTPS host")
    require(not parsed.query and not parsed.fragment and not parsed.username, "Use clean public resource URLs without account or booking parameters")

def map_url(value):
    text(value)
    parsed = urlparse(value)
    require(parsed.scheme == "https" and parsed.netloc == "www.google.com", "Map links must use the public Google Maps host")
    require(parsed.path.startswith("/maps/place/") and re.search(r"!1s0x[0-9a-f]+:0x[0-9a-f]+", parsed.path), "Use an exact checked Google Maps place, not a name search")
    require(not parsed.query and not parsed.fragment, "Remove account, search and tracking parameters from map links")
    coordinates = re.search(r"!3d(-?[\d.]+)!4d(-?[\d.]+)", parsed.path)
    require(coordinates is not None, "Map listing needs its actual destination coordinates")
    lat, lon = map(float, coordinates.groups())
    require(21.2 <= lat <= 21.75 and -158.35 <= lon <= -157.6, "Destination must be on Oahu")

def validate(data):
    fields(data, {"title", "travelers", "days", "checklist", "places", "resources"})
    text(data["title"])
    require(data["travelers"] == ["Leo", "Tyson"], "Only the public aliases Leo and Tyson are allowed")
    require(isinstance(data["places"], list), "Places must be an array")
    place_ids = set()
    lodging_ids = set()
    for place in data["places"]:
        fields(place, {"id", "name", "area", "category", "note", "address", "mapUrl"}, {"image", "imageAlt", "imageCaption"})
        for value in place.values():
            text(value)
        require(re.fullmatch(r"[a-z][a-z0-9-]*", place["id"]) and place["id"] not in place_ids, "Use unique stable place IDs")
        place_ids.add(place["id"])
        if place["category"] == "住宿":
            lodging_ids.add(place["id"])
        map_url(place["mapUrl"])
        if "image" in place:
            require(place["image"] in PUBLIC_IMAGES and "imageAlt" in place, "Use reviewed local place images with alt text")
    require(isinstance(data["days"], list) and len(data["days"]) == 8, "Keep exactly eight relative days")
    for number, day in enumerate(data["days"], 1):
        fields(day, {"id", "shortTitle", "title", "area", "summary", "transport", "image", "imageAlt", "stops", "note", "lodging"})
        require(day["id"] == f"day-{number}", "Use day-1 through day-8 in order")
        for key in ("shortTitle", "title", "area", "summary", "transport", "imageAlt", "note"):
            text(day[key])
        require(day["image"] in PUBLIC_IMAGES, "Image must be a reviewed local asset")
        require(isinstance(day["stops"], list) and day["stops"], "Each day needs at least one stop")
        require(isinstance(day["lodging"], list) and day["lodging"] and all(id in lodging_ids for id in day["lodging"]), "Lodging must refer to public hotel entries")
        for stop in day["stops"]:
            fields(stop, {"period", "name", "note", "status"}, {"placeId", "url"})
            for key in ("period", "name", "note"):
                text(stop[key])
            require(stop["status"] in STATUSES, "Unknown stop status")
            if "placeId" in stop:
                require(stop["placeId"] in place_ids, "Stop must refer to an existing checked place")
            if "url" in stop:
                url(stop["url"])
    require(isinstance(data["checklist"], list), "Checklist must be an array")
    for task in data["checklist"]:
        fields(task, {"title", "owners", "status", "note"}, {"url"})
        text(task["title"])
        text(task["note"])
        require(isinstance(task["owners"], list) and task["owners"] and set(task["owners"]) <= OWNERS, "Use only the public owner aliases")
        require(task["status"] in STATUSES, "Unknown task status")
        if "url" in task:
            url(task["url"])
    for resource in data["resources"]:
        fields(resource, {"title", "note", "url"})
        text(resource["title"])
        text(resource["note"])
        url(resource["url"])
    serialized = json.dumps(data, ensure_ascii=False)
    forbidden = [
        (r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "email address"),
        (r"\b20\d{2}[-/]\d{1,2}[-/]\d{1,2}\b|\b\d{1,2}/\d{1,2}\b", "calendar date"),
        (r"calendar\.google|group\.calendar|maps\.app\.goo\.gl|/maps/[^\s]*list|goo\.gl/maps|docs\.google|drive\.google", "private or ambiguous Google link"),
        (r"BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+", "credential"),
        (r"/Users/|/home/|file://|localhost|127\.0\.0\.1", "local machine detail"),
    ]
    for pattern, label in forbidden:
        require(not re.search(pattern, serialized, re.I), f"Public data contains a possible {label}")
    return data

if __name__ == "__main__":
    data = validate(json.loads((ROOT / "data/trip.json").read_text(encoding="utf-8")))
    print(f"Validated: {len(data['days'])} days, {len(data['places'])} places, {len(data['checklist'])} shared tasks")
