"""Build a small demo knowledge graph for ten epilepsy / synaptic genes from the raw files in data/raw.

Outputs nodes.tsv, edges.tsv and graph.json next to this script.
Only structured sources are used, so every edge is evidence_type "observed".
"""
import csv, json, math, os, re
from collections import defaultdict
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "raw")
RETRIEVED = "2026-10-03"
GENES = ["SYT1", "STXBP1", "STX1B", "SYNGAP1", "SCN1A", "SCN2A", "SCN3A", "SCN8A", "KCNQ2", "KCNQ3"]
MAX_SYMPTOMS = 30


def raw(*p):
    return os.path.join(RAW, *p)


# --- MONDO: names and exact cross-references
mondo_name, exact = {}, {}
cur, name, obsolete, xrefs = None, None, False, []


def flush():
    if cur and cur.startswith("MONDO:") and not obsolete:
        mondo_name[cur] = name
        for x in xrefs:
            exact.setdefault(x, cur)


with open(raw("mondo", "mondo.obo"), encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("["):
            flush()
            cur, name, obsolete, xrefs = None, None, False, []
        elif line.startswith("id: "):
            cur = line[4:]
        elif line.startswith("name: "):
            name = line[6:]
        elif line.startswith("is_obsolete: true"):
            obsolete = True
        elif line.startswith("xref: ") and "MONDO:equivalentTo" in line:
            xrefs.append(line[6:].split(" ")[0])
    flush()


def disease_key(raw_id):
    return exact.get(raw_id.replace("ORPHA:", "Orphanet:"), raw_id)


# --- HPO term names
hpo_name, cur = {}, None
with open(raw("hpo", "hp.obo"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("id: HP:"):
            cur = line[4:].strip()
        elif line.startswith("name: ") and cur and cur not in hpo_name:
            hpo_name[cur] = line[6:].strip()

# --- HGNC ids
hgnc, entrez = {}, {}
with open(raw("hgnc", "hgnc_complete_set.txt"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        if r["symbol"] in GENES:
            hgnc[r["symbol"]] = r["hgnc_id"]
            entrez[r["entrez_id"]] = r["symbol"]

nodes, edges = {}, []


def node(i, typ, name, **attrs):
    if i not in nodes:
        nodes[i] = {"id": i, "type": typ, "name": name, "attributes": attrs}
    else:
        nodes[i]["attributes"].update(attrs)


def edge(s, p, o, source, source_id, url, code="", **attrs):
    edges.append({"edge_id": f"E{len(edges) + 1:04d}", "subject": s, "predicate": p, "object": o, "source": source,
                  "source_id": source_id, "source_url": url, "retrieved_date": RETRIEVED, "evidence_type": "observed",
                  "evidence_code": code, "confidence": "", "quote": "", "contradicted_by": "", "attributes": attrs})


for g in GENES:
    node(hgnc[g], "gene", g)

# --- Orphanet: gene-disease association type (carries loss / gain of function where stated)
orpha_assoc = {}
for _, el in ET.iterparse(raw("orphanet", "en_product6_genes.xml"), events=("end",)):
    if el.tag == "Disorder" and el.find("OrphaCode") is not None:
        code = el.findtext("OrphaCode")
        for a in el.iter("DisorderGeneAssociation"):
            s = a.findtext("Gene/Symbol")
            if s in GENES:
                orpha_assoc[(s, "ORPHA:" + code)] = a.findtext("DisorderGeneAssociationType/Name")
        el.clear()

# --- gene -> disease (HPO aggregate of OMIM and Orphanet)
slice_raw = defaultdict(set)  # merged disease id -> raw ids
seen = set()
with open(raw("hpo", "genes_to_disease.txt"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        g = r["gene_symbol"]
        if g not in GENES:
            continue
        d = disease_key(r["disease_id"])
        slice_raw[d].add(r["disease_id"])
        assoc = orpha_assoc.get((g, r["disease_id"]), "")
        effect = "gain of function" if "gain of function" in assoc else "loss of function" if "loss of function" in assoc else ""
        if (g, d, r["disease_id"]) in seen:
            continue
        seen.add((g, d, r["disease_id"]))
        rid = r["disease_id"]
        url = ("https://www.orpha.net/en/disease/detail/" + rid.split(":")[1]) if rid.startswith("ORPHA") else ("https://omim.org/entry/" + rid.split(":")[1])
        edge(hgnc[g], "gene_associated_with_condition", d, "Orphanet" if rid.startswith("ORPHA") else "OMIM via HPO", rid, url,
             code=r["association_type"], orphanet_association=assoc, variant_effect=effect)

# --- disease -> symptom
N, term_global, dis_terms, dis_label = set(), defaultdict(set), defaultdict(dict), {}
raw_to_merged = {r: d for d, rs in slice_raw.items() for r in rs}
cols = None
with open(raw("hpo", "phenotype.hpoa"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("#"):
            continue
        p = line.rstrip("\n").split("\t")
        if cols is None:
            cols = p
            continue
        r = dict(zip(cols, p))
        N.add(r["database_id"])
        if r["aspect"] != "P" or r["qualifier"] == "NOT":
            continue
        term_global[r["hpo_id"]].add(r["database_id"])
        if r["database_id"] in raw_to_merged:
            d = raw_to_merged[r["database_id"]]
            dis_label.setdefault(d, r["disease_name"])
            dis_terms[d].setdefault(r["hpo_id"], r)

for d, raws in slice_raw.items():
    node(d, "disease", mondo_name.get(d) or dis_label.get(d) or d, source_ids=sorted(raws), n_symptoms=len(dis_terms.get(d, {})))

ic = {t: -math.log(len(ds) / len(N)) for t, ds in term_global.items()}
shared = defaultdict(set)
for d, terms in dis_terms.items():
    for t in terms:
        shared[t].add(d)
picked = sorted((t for t, ds in shared.items() if len(ds) >= 2), key=lambda t: -ic[t])[:MAX_SYMPTOMS]
for t in picked:
    node(t, "symptom", hpo_name.get(t, t), information_content=round(ic[t], 2), diseases_annotated=len(term_global[t]))
    for d in sorted(shared[t]):
        r = dis_terms[d][t]
        edge(d, "has_phenotype", t, "HPO annotations", r["database_id"], "https://hpo.jax.org/browse/term/" + t,
             code=r["evidence"], frequency=r["frequency"], reference=r["reference"])

# --- gene -> pathway
with open(raw("reactome", "NCBI2Reactome.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if p[0] in entrez and p[5] == "Homo sapiens":
            pid = "REACT:" + p[1]
            node(pid, "pathway", p[3].strip())
            edge(hgnc[entrez[p[0]]], "participates_in", pid, "Reactome", p[1], p[2], code=p[4])

# --- write
ncols = ["id", "type", "name", "attributes"]
ecols = ["edge_id", "subject", "predicate", "object", "source", "source_id", "source_url", "retrieved_date", "evidence_type",
         "evidence_code", "confidence", "quote", "contradicted_by", "attributes"]
for fn, rows, cs in [("nodes.tsv", nodes.values(), ncols), ("edges.tsv", edges, ecols)]:
    with open(os.path.join(HERE, fn), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(cs)
        for r in rows:
            w.writerow([json.dumps(r[c], ensure_ascii=False) if c == "attributes" else r[c] for c in cs])
with open(os.path.join(HERE, "graph.json"), "w", encoding="utf-8") as f:
    json.dump({"nodes": list(nodes.values()), "edges": edges}, f, ensure_ascii=False)

from collections import Counter
print("nodes", len(nodes), dict(Counter(n["type"] for n in nodes.values())))
print("edges", len(edges), dict(Counter(e["predicate"] for e in edges)))
print("edges with a stated variant effect:", [(nodes[e["subject"]]["name"], nodes[e["object"]]["name"], e["attributes"]["variant_effect"]) for e in edges if e["attributes"].get("variant_effect")])
print("diseases not mapped to MONDO:", [d for d in slice_raw if not d.startswith("MONDO")])
