"""Step 9: write views/atlas_cluster_view.html, the one user interface, from views/src/atlas.template.html.

It embeds five things, so the page is a single file that opens offline:
  data/atlas/atlas_view.json   every disease, its mechanism cluster and nearest neighbours
  data/slice/slice_view.json   the journey for the slice: leads, evidence, groups, studies, people, gaps, explanations
  a symptom index              every HPO symptom in the atlas with the diseases that have it, for the global search
  atlas links                  the sources behind each map line outside the slice: gene to disease (OMIM, Orphanet),
                               gene to the pathways neighbours share (Reactome), and the HPO id of each shared symptom
  views/src/vendor/force-graph.min.js the force-directed graph library that draws the map (MIT licence, header kept)
"""
import json, os
from collections import defaultdict
from common import ATLAS, ROOT, SLICE, read_tsv

atlas = json.load(open(os.path.join(ATLAS, "atlas_view.json"), encoding="utf-8"))
sl = json.load(open(os.path.join(SLICE, "slice_view.json"), encoding="utf-8"))
idx = {d[0]: i for i, d in enumerate(atlas["d"])}
nodes = read_tsv(os.path.join(ATLAS, "nodes.tsv"))
name = {r["id"]: r["name"] for r in nodes if r["type"] in ("symptom", "pathway", "gene")}
path_idx = {p: i for i, p in enumerate(atlas["paths"])}   # the compact view names pathways; two names are shared by two Reactome ids each
term_idx = {t: i for i, t in enumerate(atlas["terms"])}
path_id, term_id = [""] * len(path_idx), [""] * len(term_idx)
for r in nodes:
    if r["type"] == "pathway" and r["name"] in path_idx and not path_id[path_idx[r["name"]]]:
        path_id[path_idx[r["name"]]] = r["id"].removeprefix("REACT:")
    if r["type"] == "symptom" and r["name"] in term_idx and not term_id[term_idx[r["name"]]]:
        term_id[term_idx[r["name"]]] = r["id"]

by_symptom = defaultdict(set)
gene_paths = defaultdict(set)      # symbol -> indices of the pathways in the compact view
gene_links = [[] for _ in atlas["d"]]   # disease index -> [symbol, "OMIM" | "ORPHA", id, association type]
retrieved = ""
for e in read_tsv(os.path.join(ATLAS, "edges.tsv.gz")):
    p, retrieved = e["predicate"], e["retrieved_date"]
    if p == "has_phenotype" and e["subject"] in idx:
        by_symptom[e["object"]].add(idx[e["subject"]])
    elif p == "participates_in" and name.get(e["object"]) in path_idx:
        gene_paths[name[e["subject"]]].add(path_idx[name[e["object"]]])
    elif p == "gene_associated_with_condition" and e["object"] in idx:
        pre, _, num = e["source_id"].partition(":")
        gene_links[idx[e["object"]]].append([name[e["subject"]], pre, num, e["evidence_code"]])
symptoms = sorted([[name.get(t, t), sorted(ds)] for t, ds in by_symptom.items()], key=lambda x: (-len(x[1]), x[0]))
links = {"gp": {g: sorted(ps) for g, ps in sorted(gene_paths.items())}, "pu": path_id, "tu": term_id, "gd": gene_links, "date": retrieved}

dump = lambda x: json.dumps(x, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
with open(os.path.join(ROOT, "views", "src", "atlas.template.html"), encoding="utf-8") as f:
    page = f.read()
with open(os.path.join(ROOT, "views", "src", "vendor", "force-graph.min.js"), encoding="utf-8") as f:
    force_graph = f.read()
for key, value in (("__ATLAS__", dump(atlas)), ("__SLICE__", dump(sl)), ("__SYMPTOMS__", dump(symptoms)), ("__LINKS__", dump(links)), ("__FORCEGRAPH__", force_graph)):
    assert page.count(key) == 1, key
    page = page.replace(key, value)
out = os.path.join(ROOT, "views", "atlas_cluster_view.html")
with open(out, "w", encoding="utf-8") as f:
    f.write(page)
print("wrote", os.path.relpath(out, ROOT), round(len(page) / 1e6, 2), "MB |", len(atlas["d"]), "diseases,", len(sl["diseases"]), "with the full journey,", len(symptoms), "symptoms")
