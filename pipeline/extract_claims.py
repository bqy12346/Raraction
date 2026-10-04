"""Step 6 (OpenAI): read mechanism claims and research assets out of the PubMed abstracts.

For each abstract the model returns claims about a slice gene: the mechanism (loss of function, gain of function,
dominant negative), the kind of evidence (patients, animal model, cells), any reusable asset it describes (a mouse model,
a compound, a biomarker), and which slice disease it is about, chosen from a list of ids (the reconcile step).
Nothing is trusted as returned:
  - the quote must appear word for word in the abstract, or the claim is dropped
  - the gene must be the one the paper was fetched for, and the disease id must come from the list offered
Claims become edges with evidence_type "extracted". Claims on the same gene that point to opposite mechanisms
are linked through contradicted_by. Writes data/slice/parts/extract_{nodes,edges}.tsv and a report of what was dropped.
"""
import json, os, re, sys
from collections import Counter, defaultdict
from common import SLICE, Graph, load_slice, obj, openai_json

MECHS = ["loss_of_function", "gain_of_function", "dominant_negative", "mixed_or_unclear", "not_about_mechanism"]
LEVELS = ["patients", "patient_cells", "animal_model", "cell_model", "in_vitro_biochemistry", "computational", "review"]
ASSET_KINDS = ["none", "animal_model", "cell_line", "compound", "biomarker", "outcome_measure", "registry_or_cohort", "gene_therapy_vector"]
SCHEMA = obj(
    about_human_gene=({"type": "boolean"}),
    claims={"type": "array", "items": obj(
        gene={"type": "string"},
        disease_id={"type": "string"},
        mechanism={"type": "string", "enum": MECHS},
        statement={"type": "string"},
        quote={"type": "string"},
        evidence_level={"type": "string", "enum": LEVELS},
        confidence={"type": "number"},
        asset_kind={"type": "string", "enum": ASSET_KINDS},
        asset_name={"type": "string"})})
SYSTEM = """You extract evidence for a rare-disease knowledge graph. Read one PubMed abstract and return claims about the named genes only.
Rules:
- Only state what the abstract itself reports or concludes. Never add outside knowledge.
- quote must be copied character for character from the abstract (one sentence or clause). Do not paraphrase inside quote.
- mechanism: loss_of_function covers haploinsufficiency, reduced expression or activity; gain_of_function covers increased or new activity;
  dominant_negative means the mutant protein interferes with the normal one. Use not_about_mechanism for claims on phenotype, models or therapy.
- disease_id must be one of the ids offered, or "" when the abstract does not name one of those diseases.
- asset_kind/asset_name: a reusable research resource the abstract describes (mouse or zebrafish model, iPSC line, compound tested,
  biomarker, outcome measure, cohort or registry, gene therapy vector). Use "none" and "" otherwise.
- confidence: how strongly the abstract supports the claim (0.9 direct experimental or patient evidence, 0.6 suggestive, 0.3 speculation).
- statement: one plain-English sentence a parent could follow.
- If the abstract is not about the human gene (for example an acronym with the same letters), set about_human_gene false and return no claims.
Return at most 4 claims, the most useful first."""

sl = load_slice()
gene_id = {g["symbol"]: g["id"] for g in sl["genes"]}
diseases_of = defaultdict(list)
for d in sl["diseases"]:
    for s in d["genes"]:
        diseases_of[s].append(d)
with open(os.path.join(SLICE, "parts", "pubmed_abstracts.json"), encoding="utf-8") as f:
    abstracts = json.load(f)
squash = lambda s: re.sub(r"\s+", " ", s).strip().lower()

g = Graph("extract")
dropped, model_used = Counter(), set()
by_gene = defaultdict(list)   # gene -> [(edge index, mechanism)]
for pmid, a in sorted(abstracts.items()):
    if not a["abstract"]:
        continue
    offered = {d["id"]: d for s in a["genes"] for d in diseases_of[s]}
    user = (f"Genes: {', '.join(a['genes'])}\n"
            f"Disease ids you may use:\n" + "\n".join(f"- {i}: {d['name']}" + (f" (also: {'; '.join(d['synonyms'][:4])})" if d["synonyms"] else "") for i, d in offered.items()) +
            f"\n\nPMID {pmid} ({a['year']})\nTitle: {a['title']}\nAbstract:\n{a['abstract']}")
    try:
        out, retrieved, model = openai_json(f"claims-{pmid}", SYSTEM, user, "claims", SCHEMA)
    except RuntimeError as ex:
        sys.exit(f"stopped at PMID {pmid}: {ex}")
    model_used.add(model)
    if not out["about_human_gene"]:
        dropped["not about the human gene"] += 1
        continue
    src = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    for c in out["claims"]:
        if c["gene"] not in a["genes"]:
            dropped["gene not in the paper's slice genes"] += 1
            continue
        if squash(c["quote"]) not in squash(a["title"] + " " + a["abstract"]) or len(c["quote"]) < 20:
            dropped["quote not found in abstract"] += 1
            continue
        if c["disease_id"] and c["disease_id"] not in offered:
            dropped["disease id not offered (cleared)"] += 1
            c["disease_id"] = ""
        common = dict(confidence=max(0.0, min(1.0, c["confidence"])), quote=c["quote"], statement=c["statement"], evidence_level=c["evidence_level"],
                      disease_id=c["disease_id"], model=model)
        if c["mechanism"] in ("loss_of_function", "gain_of_function", "dominant_negative"):
            mid = "MECH:" + c["mechanism"]
            g.node(mid, "mechanism", c["mechanism"].replace("_", " "))
            g.edge(gene_id[c["gene"]], "has_mechanism", mid, "PubMed (extracted by OpenAI)", pmid, src, retrieved, "extracted", c["evidence_level"], **common)
            by_gene[c["gene"]].append((len(g.edges) - 1, c["mechanism"]))
        if c["asset_kind"] != "none" and c["asset_name"].strip():
            aid = "ASSET:" + re.sub(r"[^a-z0-9]+", "-", (c["gene"] + " " + c["asset_name"]).lower()).strip("-")[:70]
            g.node(aid, "asset", c["asset_name"].strip(), asset_kind=c["asset_kind"], gene=c["gene"])
            g.edge("PMID:" + pmid, "describes_asset", aid, "PubMed (extracted by OpenAI)", pmid, src, retrieved, "extracted", c["evidence_level"], **common)
            g.edge(aid, "asset_for_gene", gene_id[c["gene"]], "PubMed (extracted by OpenAI)", pmid, src, retrieved, "extracted", c["evidence_level"], **common)
        if c["disease_id"] and c["mechanism"] in ("loss_of_function", "gain_of_function", "dominant_negative"):
            g.edge(c["disease_id"], "caused_by_mechanism", "MECH:" + c["mechanism"], "PubMed (extracted by OpenAI)", pmid, src, retrieved, "extracted",
                   c["evidence_level"], gene=c["gene"], **common)

# opposite mechanisms on the same gene contradict each other; dominant negative and loss of function call for different therapies
OPPOSED = {("loss_of_function", "gain_of_function"), ("loss_of_function", "dominant_negative"), ("gain_of_function", "dominant_negative")}
for i, e in enumerate(g.edges):
    e[0] = f"EXT{i + 1:06d}"
for sym, items in by_gene.items():
    for i, m in items:
        against = [g.edges[j][0] for j, n in items if tuple(sorted((m, n))) in OPPOSED]
        g.edges[i][12] = "|".join(against)
g.write()
print("model:", model_used, "| dropped:", dict(dropped))
print("mechanism claims per gene:", {s: dict(Counter(m for _, m in v)) for s, v in by_gene.items()})
