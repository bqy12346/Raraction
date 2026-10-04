"""Step 9: embed data/slice/slice_view.json into views/src/journey.template.html and write views/journey.html (one file, opens offline)."""
import json, os
from common import ROOT, SLICE

with open(os.path.join(SLICE, "slice_view.json"), encoding="utf-8") as f:
    data = json.dumps(json.load(f), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
with open(os.path.join(ROOT, "views", "src", "journey.template.html"), encoding="utf-8") as f:
    page = f.read().replace("__DATA__", data, 1)
out = os.path.join(ROOT, "views", "journey.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", os.path.relpath(out, ROOT), round(len(page) / 1e6, 2), "MB")
