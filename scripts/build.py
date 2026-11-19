"""Build an explicit allowlist of public files; never copy the whole checkout."""
import json
import shutil
from pathlib import Path
from validate import ROOT, validate

validate(json.loads((ROOT / "data/trip.json").read_text(encoding="utf-8")))
destination = ROOT / "dist"
destination.mkdir(exist_ok=True)
files = [
    "index.html", "styles.css", "app.js", "CREDITS.html", "data/trip.json",
    "assets/waikiki.jpg", "assets/kualoa-ranch.jpg", "assets/hanauma-bay.jpg",
]
for relative in files:
    target = destination / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / relative, target)
(destination / ".nojekyll").touch()
expected = set(files) | {".nojekyll"}
actual = {str(path.relative_to(destination)) for path in destination.rglob("*") if path.is_file()}
if actual != expected:
    raise ValueError("Build output contains unexpected files; use a clean dist directory")
print(f"Built {len(expected)} reviewed public files")
