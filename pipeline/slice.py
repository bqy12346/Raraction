"""Step 0: pick the demo slice out of the atlas and copy its part of the graph.

The slice is the seed disease (STXBP1 encephalopathy), its atlas neighbours, and every disease caused by their core genes.
Core genes are the genes of those diseases, leaving out umbrella diseases that list more than MAX_GENES genes.
Writes data/slice/slice.json and data/slice/parts/atlas_{nodes,edges}.tsv. Disease synonyms come from MONDO through the EBI OLS API.
"""
import json, os
from collections import defaultdict
from common import ATLAS, SLICE, Graph, cached, read_tsv, url

SEED = "MONDO:0012812"
MAX_GENES = 3

nodes = {r["id"]: r for r in read_tsv(os.path.join(ATLAS, "nodes.tsv"))}
cls = {r["disease_id"]: r for r in read_tsv(os.path.join(ATLAS, "disease_classification.tsv"))}
nbr_rows = read_tsv(os.path.join(ATLAS, "disease_neighbors.tsv"))
edges = read_tsv(os.path.join(ATLAS, "edges.tsv.gz"))
sym2hgnc = {n["name"]: i for i, n in nodes.items() if n["type"] == "gene"}

first = {SEED} | {r["disease_b"] for r in nbr_rows if r["disease_a"] == SEED} | {r["disease_a"] for r in nbr_rows if r["disease_b"] == SEED}
genes = {sym2hgnc[s] for d in first for s in cls[d]["genes"].split("|") if len(cls[d]["genes"].split("|")) <= MAX_GENES}
gene_dis = defaultdict(set)
for e in edges:
    if e["predicate"] == "gene_associated_with_condition":
        gene_dis[e["subject"]].add(e["object"])
diseases = first | {d for g in genes for d in gene_dis[g]}

# ---------------------------------------------------------------- copy the atlas edges that touch the slice
g = Graph("atlas")
keep = []
for e in edges:
    p, s, o = e["predicate"], e["subject"], e["object"]
    if (p == "gene_associated_with_condition" and s in genes and o in diseases) or (p == "has_phenotype" and s in diseases) or (p == "participates_in" and s in genes):
        keep.append(e)
for e in keep:
    for nid in (e["subject"], e["object"]):
        n = nodes[nid]
        g.node(nid, n["type"], n["name"], **json.loads(n["attributes"]))
    g.edge(e["subject"], e["predicate"], e["object"], e["source"], e["source_id"], e["source_url"], e["retrieved_date"], e["evidence_type"], e["evidence_code"],
           atlas_edge_id=e["edge_id"], **json.loads(e["attributes"]))
for d in diseases:   # umbrella diseases keep their node even when their genes are outside the slice
    g.node(d, "disease", nodes[d]["name"], **json.loads(nodes[d]["attributes"]))

# neighbour pairs are computed, not observed: they are hypotheses for a person to check
for r in nbr_rows:
    a, b = r["disease_a"], r["disease_b"]
    if a in diseases and b in diseases:
        g.edge(a, "similar_mechanism_and_phenotype", b, "Raraction neighbour score", f"{a}~{b}", "data/atlas/disease_neighbors.tsv", "2026-10-03", "inferred",
               "pathway+HPO overlap", confidence=(float(r["mechanism_similarity"]) * float(r["phenotype_similarity"])) ** 0.5,
               mechanism_similarity=float(r["mechanism_similarity"]), phenotype_similarity=float(r["phenotype_similarity"]), same_gene=r["same_gene"] == "1",
               shared_pathways=[x for x in r["top_shared_pathways"].split("|") if x], shared_symptoms=[x for x in r["top_shared_symptoms"].split("|") if x])
g.write()

# ---------------------------------------------------------------- synonyms from MONDO (EBI OLS) for search and for querying other sources
OLS = "https://www.ebi.ac.uk/ols4/api/ontologies/mondo/terms"
out = {"seed": SEED, "genes": [], "diseases": []}
for h in sorted(genes, key=lambda h: nodes[h]["name"]):
    a = json.loads(nodes[h]["attributes"])
    out["genes"].append({"id": h, "symbol": nodes[h]["name"], "name": a.get("full_name", ""), "ncbi_gene_id": a.get("ncbi_gene_id", "")})
for d in sorted(diseases):
    syn = []
    if d.startswith("MONDO:"):
        res, _ = cached("ols", d, url(OLS, obo_id=d))
        for t in res.get("_embedded", {}).get("terms", []):
            syn += t.get("synonyms") or []
    c = cls.get(d, {})
    out["diseases"].append({"id": d, "name": nodes[d]["name"], "genes": [s for s in c.get("genes", "").split("|") if s], "direction": c.get("direction", ""),
                            "mechanism_class": c.get("mechanism_class", ""), "in_first_ring": d in first, "synonyms": sorted(set(syn) - {nodes[d]["name"]})})
with open(os.path.join(SLICE, "slice.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("slice:", len(out["genes"]), "genes", [x["symbol"] for x in out["genes"]], "|", len(out["diseases"]), "diseases,", len(first), "in the first ring")
