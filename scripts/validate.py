"""Validate the editable public itinerary before publication (standard library only)."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
STATUSES = {"planned", "pending", "confirmed", "optional"}
OWNERS = {"Leon", "Tyson"}
ALLOWED_HOSTS = {
    "www.gojumphawaii.com", "www.honolulu.gov", "www.kualoa.com",
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

def validate(data):
    fields(data, {"title", "travelers", "days", "checklist", "places", "resources"})
    text(data["title"])
    require(data["travelers"] == ["Leon", "Tyson"], "Only the public aliases Leon and Tyson are allowed")
    require(isinstance(data["days"], list) and len(data["days"]) == 8, "Keep exactly eight relative days")
    for number, day in enumerate(data["days"], 1):
        fields(day, {"id", "shortTitle", "title", "area", "summary", "transport", "image", "imageAlt", "stops", "note"})
        require(day["id"] == f"day-{number}", "Use day-1 through day-8 in order")
        for key in ("shortTitle", "title", "area", "summary", "transport", "imageAlt", "note"):
            text(day[key])
        require(day["image"] in {"./assets/waikiki.jpg", "./assets/kualoa-ranch.jpg", "./assets/hanauma-bay.jpg"}, "Image must be a reviewed local asset")
        require(isinstance(day["stops"], list) and day["stops"], "Each day needs at least one stop")
        for stop in day["stops"]:
            fields(stop, {"period", "name", "note", "status"}, {"mapQuery", "url"})
            for key in ("period", "name", "note"):
                text(stop[key])
            require(stop["status"] in STATUSES, "Unknown stop status")
            if "mapQuery" in stop:
                text(stop["mapQuery"])
                require(not re.search(r"hotel|garden inn|private residence", stop["mapQuery"], re.I), "Do not publish lodging or private pickup points")
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
    require(isinstance(data["places"], list), "Places must be an array")
    for place in data["places"]:
        fields(place, {"name", "area", "category", "note", "mapQuery"})
        for value in place.values():
            text(value)
        require(not re.search(r"hotel|garden inn|private residence", place["mapQuery"], re.I), "Do not publish lodging or private pickup points")
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
