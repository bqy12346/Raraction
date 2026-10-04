"""Step 9: write views/atlas_cluster_view.html, the one user interface, from views/src/atlas.template.html.

It embeds three things, so the page is a single file that opens offline:
  data/atlas/atlas_view.json   every disease, its mechanism cluster and nearest neighbours
  data/slice/slice_view.json   the journey for the slice: leads, evidence, groups, studies, people, gaps, explanations
  a symptom index              every HPO symptom in the atlas with the diseases that have it, for the global search
"""
import json, os
from collections import defaultdict
from common import ATLAS, ROOT, SLICE, read_tsv

atlas = json.load(open(os.path.join(ATLAS, "atlas_view.json"), encoding="utf-8"))
sl = json.load(open(os.path.join(SLICE, "slice_view.json"), encoding="utf-8"))
idx = {d[0]: i for i, d in enumerate(atlas["d"])}
name = {r["id"]: r["name"] for r in read_tsv(os.path.join(ATLAS, "nodes.tsv")) if r["type"] == "symptom"}
by_symptom = defaultdict(set)
for e in read_tsv(os.path.join(ATLAS, "edges.tsv.gz")):
    if e["predicate"] == "has_phenotype" and e["subject"] in idx:
        by_symptom[e["object"]].add(idx[e["subject"]])
symptoms = sorted([[name.get(t, t), sorted(ds)] for t, ds in by_symptom.items()], key=lambda x: (-len(x[1]), x[0]))

dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
with open(os.path.join(ROOT, "views", "src", "atlas.template.html"), encoding="utf-8") as f:
    page = f.read()
for key, value in (("__ATLAS__", atlas), ("__SLICE__", sl), ("__SYMPTOMS__", symptoms)):
    assert page.count(key) == 1, key
    page = page.replace(key, dump(value))
out = os.path.join(ROOT, "views", "atlas_cluster_view.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", os.path.relpath(out, ROOT), round(len(page) / 1e6, 2), "MB |", len(atlas["d"]), "diseases,", len(sl["diseases"]), "with the full journey,", len(symptoms), "symptoms")
