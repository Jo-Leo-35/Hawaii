"""Build an explicit allowlist of public files; never copy the whole checkout."""
import json
import shutil
from pathlib import Path
from validate import ROOT, validate, PUBLIC_IMAGES

validate(json.loads((ROOT / "data/trip.json").read_text(encoding="utf-8")))
destination = ROOT / "dist"
destination.mkdir(exist_ok=True)
files = [
    "index.html", "styles.css", "app.js", "CREDITS.html", "data/trip.json",

]
files += sorted(image.removeprefix("./") for image in PUBLIC_IMAGES)
files += ["assets/icons/" + name + ".svg" for name in ["fork-knife", "shopping-bag", "bed", "bus", "mountains", "person-simple-run", "magnifying-glass", "map-pin", "calendar-blank", "check-circle"]]
files += ["assets/icons/LICENSE.txt"]
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
