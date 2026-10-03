"""Build the cross-referenced atlas database from data/raw and classify every disease by mechanism and phenotype.

Outputs (next to this script):
  crosswalk_genes.tsv, crosswalk_diseases.tsv   translation tables for the two join keys
  nodes.tsv, edges.tsv                          the knowledge graph, one source per edge
  disease_classification.tsv                    mechanism class, phenotype class, direction, centrality
  disease_neighbors.tsv                         disease pairs that share a pathway, with both similarity scores
  atlas_view.json                               compact data for the web view
Only structured sources are used, so every edge is evidence_type "observed".
"""
import csv, json, math, os, re, sys
from collections import Counter, defaultdict
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "raw")
RETRIEVED = "2026-10-03"
MAX_PATHWAY_DISEASES = 60   # pathways larger than this are too broad to propose neighbours
TOP_NEIGHBORS = 10
MIN_PHENO, MIN_MECH = 0.10, 0.10


def raw(*p):
    return os.path.join(RAW, *p)


def bare(x):
    return x.split(":")[-1]


def tsv(name, cols, rows):
    with open(os.path.join(HERE, name), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t")
        w.writerow(cols)
        w.writerows(rows)


# ---------------------------------------------------------------- genes
entrez2hgnc, gene = {}, {}
with open(raw("hgnc", "hgnc_complete_set.txt"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        gene[r["hgnc_id"]] = r
        if r["entrez_id"]:
            entrez2hgnc[r["entrez_id"]] = r["hgnc_id"]
sym2hgnc = {r["symbol"]: h for h, r in gene.items()}

# ---------------------------------------------------------------- diseases (MONDO)
mondo, exact = {}, {}
cur = None


def flush():
    if cur and cur["id"].startswith("MONDO:") and not cur["obs"]:
        mondo[cur["id"]] = cur
        for x in cur["xref"]:
            exact.setdefault(x, cur["id"])


with open(raw("mondo", "mondo.obo"), encoding="utf-8") as f:
    for line in f:
        line = line.rstrip("\n")
        if line.startswith("["):
            flush()
            cur = {"id": "", "name": "", "obs": False, "xref": [], "syn": 0} if line == "[Term]" else None
        elif cur is None:
            continue
        elif line.startswith("id: "):
            cur["id"] = line[4:]
        elif line.startswith("name: "):
            cur["name"] = line[6:]
        elif line.startswith("is_obsolete: true"):
            cur["obs"] = True
        elif line.startswith("synonym: "):
            cur["syn"] += 1
        elif line.startswith("xref: ") and "MONDO:equivalentTo" in line:
            cur["xref"].append(line[6:].split(" ")[0])
    flush()


def disease_key(raw_id):
    return exact.get(raw_id.replace("ORPHA:", "Orphanet:"), raw_id)


# ---------------------------------------------------------------- Orphanet gene associations
orpha = {}
for _, el in ET.iterparse(raw("orphanet", "en_product6_genes.xml"), events=("end",)):
    if el.tag == "Disorder" and el.find("OrphaCode") is not None:
        code = "ORPHA:" + el.findtext("OrphaCode")
        for a in el.iter("DisorderGeneAssociation"):
            orpha[(a.findtext("Gene/Symbol"), code)] = (a.findtext("DisorderGeneAssociationType/Name") or "", a.findtext("SourceOfValidation") or "")
        el.clear()

# ---------------------------------------------------------------- gene -> disease (causal links only)
dis_genes, dis_raw, gd_rows, skipped = defaultdict(set), defaultdict(set), [], 0
dis_effect = defaultdict(set)
with open(raw("hpo", "genes_to_disease.txt"), encoding="utf-8") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        h = entrez2hgnc.get(bare(r["ncbi_gene_id"]))
        rid = r["disease_id"]
        assoc, src = orpha.get((r["gene_symbol"], rid), ("", ""))
        causal = r["association_type"] == "MENDELIAN" or assoc.startswith("Disease-causing germline mutation(s)")
        if not h or not causal:
            skipped += 1
            continue
        d = disease_key(rid)
        effect = "gain of function" if "gain of function" in assoc else "loss of function" if "loss of function" in assoc else ""
        if effect:
            dis_effect[d].add(effect)
        dis_genes[d].add(h)
        dis_raw[d].add(rid)
        gd_rows.append((h, d, rid, r["association_type"], assoc, effect, src))

# ---------------------------------------------------------------- HPO ontology
hp_name, hp_parents, cur_id, obs = {}, defaultdict(set), None, set()
with open(raw("hpo", "hp.obo"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("id: HP:"):
            cur_id = line[4:].strip()
        elif line.startswith("name: ") and cur_id and cur_id not in hp_name:
            hp_name[cur_id] = line[6:].strip()
        elif line.startswith("is_a: HP:") and cur_id:
            hp_parents[cur_id].add(line[6:16])
        elif line.startswith("is_obsolete: true") and cur_id:
            obs.add(cur_id)
ROOT = "HP:0000118"
_anc = {}


def ancestors(t):
    if t not in _anc:
        s = {t}
        for p in hp_parents.get(t, ()):
            s |= ancestors(p)
        _anc[t] = s
    return _anc[t]


organ_systems = sorted(t for t, ps in hp_parents.items() if ROOT in ps and t not in obs)

# ---------------------------------------------------------------- disease -> symptom
raw_terms, raw_rows, all_raw = defaultdict(set), defaultdict(dict), set()
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
        all_raw.add(r["database_id"])
        if r["aspect"] == "P" and r["qualifier"] != "NOT":
            raw_terms[r["database_id"]].add(r["hpo_id"])
            raw_rows[r["database_id"]].setdefault(r["hpo_id"], r)

# information content over ancestor-closed annotations, across every annotated disease
closed_count = Counter()
for rid, ts in raw_terms.items():
    cl = set()
    for t in ts:
        cl |= ancestors(t)
    closed_count.update(cl)
N_ANNOT = len(raw_terms)
ic = {t: -math.log(c / N_ANNOT) for t, c in closed_count.items()}

diseases = sorted(dis_genes)
dis_terms, dis_closed = {}, {}
for d in diseases:
    direct = set()
    for rid in dis_raw[d]:
        direct |= raw_terms.get(rid, set())
    dis_terms[d] = direct
    cl = set()
    for t in direct:
        cl |= ancestors(t)
    cl.discard(ROOT)
    cl.discard("HP:0000001")
    dis_closed[d] = cl


def name_of(d):
    if d in mondo:
        return mondo[d]["name"]
    for rid in dis_raw[d]:
        for r in raw_rows.get(rid, {}).values():
            return r["disease_name"]
    return d


# ---------------------------------------------------------------- pathways (Reactome)
p_name, p_parents = {}, defaultdict(set)
with open(raw("reactome", "ReactomePathways.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if p[2] == "Homo sapiens":
            p_name[p[0]] = p[1].strip()
with open(raw("reactome", "ReactomePathwaysRelation.txt"), encoding="utf-8") as f:
    for line in f:
        a, b = line.split()
        if b in p_name:
            p_parents[b].add(a)
_roots = {}


def roots(p):
    if p not in _roots:
        ps = p_parents.get(p)
        _roots[p] = {p} if not ps else set().union(*(roots(x) for x in ps))
    return _roots[p]


gene_paths, path_url, path_code = defaultdict(set), {}, {}
disease_genes_all = set().union(*dis_genes.values())
with open(raw("reactome", "NCBI2Reactome.txt"), encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        h = entrez2hgnc.get(p[0])
        if p[5] == "Homo sapiens" and h in disease_genes_all:
            gene_paths[h].add(p[1])
            path_url[p[1]] = p[2]
            path_code[(h, p[1])] = p[4]

dis_paths = {d: set().union(*(gene_paths.get(g, set()) for g in dis_genes[d])) for d in diseases}
path_dis = defaultdict(set)
for d, ps in dis_paths.items():
    for p in ps:
        path_dis[p].add(d)
n_with_path = sum(1 for d in diseases if dis_paths[d])
w = {p: -math.log(len(ds) / n_with_path) for p, ds in path_dis.items()}   # specific pathways weigh more

# ---------------------------------------------------------------- classification
def mech_class(d):
    score = Counter()
    for p in dis_paths[d]:
        rs = [r for r in roots(p) if p_name.get(r) != "Disease"]
        for r in rs:
            score[p_name.get(r, r)] += w[p] / len(rs)
    return score.most_common(1)[0][0] if score else "No pathway data"


def pheno_class(d):
    score = Counter()
    for t in dis_terms[d]:
        tops = [o for o in organ_systems if o in ancestors(t)]
        for o in tops:
            score[hp_name[o]] += ic.get(t, 0) / len(tops)
    return score.most_common(1)[0][0] if score else "No symptom data"


mclass = {d: mech_class(d) for d in diseases}
pclass = {d: pheno_class(d) for d in diseases}
direction = {d: ("both reported" if len(dis_effect[d]) > 1 else next(iter(dis_effect[d]), "")) for d in diseases}

# ---------------------------------------------------------------- neighbours: share a specific pathway, scored on both axes
ic_sum = {d: sum(ic.get(t, 0) for t in dis_closed[d]) for d in diseases}
w_sum = {d: sum(w[p] for p in dis_paths[d]) for d in diseases}
pairs = set()
for p, ds in path_dis.items():
    if 2 <= len(ds) <= MAX_PATHWAY_DISEASES:
        ds = sorted(ds)
        for i, a in enumerate(ds):
            for b in ds[i + 1:]:
                pairs.add((a, b))
scored = []
for a, b in pairs:
    sp = dis_paths[a] & dis_paths[b]
    m = sum(w[p] for p in sp)
    mech = m / (w_sum[a] + w_sum[b] - m)
    ca, cb = dis_closed[a], dis_closed[b]
    if not ca or not cb:
        continue
    small, big = (ca, cb) if len(ca) < len(cb) else (cb, ca)
    s = sum(ic.get(t, 0) for t in small if t in big)
    pheno = s / (ic_sum[a] + ic_sum[b] - s) if s else 0.0
    if mech >= MIN_MECH and pheno >= MIN_PHENO:
        scored.append((a, b, mech, pheno, bool(dis_genes[a] & dis_genes[b])))
nbrs = defaultdict(list)
for a, b, mech, pheno, same in scored:
    nbrs[a].append((b, mech, pheno, same))
    nbrs[b].append((a, mech, pheno, same))
strength = {}
for d in diseases:
    nbrs[d].sort(key=lambda x: -math.sqrt(x[1] * x[2]))
    strength[d] = sum(math.sqrt(x[1] * x[2]) for x in nbrs[d])
ranked = sorted(diseases, key=lambda d: strength[d])
centrality = {d: round(100 * i / (len(ranked) - 1)) if strength[d] else 0 for i, d in enumerate(ranked)}


def shared_evidence(a, b):
    sp = sorted(dis_paths[a] & dis_paths[b], key=lambda p: -w[p])[:2]
    st = sorted(dis_closed[a] & dis_closed[b], key=lambda t: -ic.get(t, 0))[:3]
    return sp, st


# ---------------------------------------------------------------- write crosswalks
tsv("crosswalk_genes.tsv", ["hgnc_id", "symbol", "name", "ncbi_gene_id", "ensembl_gene_id", "omim_id", "alias_symbols", "previous_symbols", "is_disease_gene"],
    [(h, r["symbol"], r["name"], r["entrez_id"], r["ensembl_gene_id"], r["omim_id"], r["alias_symbol"], r["prev_symbol"], int(h in disease_genes_all)) for h, r in gene.items()])
by_prefix = lambda m, pre: "|".join(sorted(x for x in m["xref"] if x.startswith(pre)))
tsv("crosswalk_diseases.tsv", ["mondo_id", "name", "omim_ids", "orphanet_ids", "gard_ids", "n_synonyms", "in_atlas"],
    [(i, m["name"], by_prefix(m, "OMIM:"), by_prefix(m, "Orphanet:"), by_prefix(m, "GARD:"), m["syn"], int(i in dis_genes)) for i, m in mondo.items()
     if any(x.startswith(("OMIM:", "Orphanet:", "GARD:")) for x in m["xref"])])

# ---------------------------------------------------------------- write graph
nodes, edges = [], []


def edge(s, p, o, source, source_id, url, code, attrs):
    edges.append((f"E{len(edges) + 1:07d}", s, p, o, source, source_id, url, RETRIEVED, "observed", code, "", "", "", json.dumps(attrs, ensure_ascii=False)))


for h in sorted(disease_genes_all):
    nodes.append((h, "gene", gene[h]["symbol"], json.dumps({"ncbi_gene_id": gene[h]["entrez_id"], "full_name": gene[h]["name"]})))
for d in diseases:
    nodes.append((d, "disease", name_of(d), json.dumps({"source_ids": sorted(dis_raw[d]), "mechanism_class": mclass[d], "phenotype_class": pclass[d], "direction": direction[d]})))
used_terms = set().union(*dis_terms.values())
for t in sorted(used_terms):
    nodes.append((t, "symptom", hp_name.get(t, t), json.dumps({"information_content": round(ic.get(t, 0), 2)})))
for p in sorted(path_dis):
    nodes.append(("REACT:" + p, "pathway", p_name.get(p, p), json.dumps({"top_level": sorted(p_name.get(r, r) for r in roots(p)), "n_diseases": len(path_dis[p])})))

for h, d, rid, atype, assoc, effect, src in gd_rows:
    url = ("https://www.orpha.net/en/disease/detail/" + bare(rid)) if rid.startswith("ORPHA") else ("https://omim.org/entry/" + bare(rid))
    edge(h, "gene_associated_with_condition", d, "Orphanet" if rid.startswith("ORPHA") else "OMIM via HPO", rid, url, atype,
         {"orphanet_association": assoc, "variant_effect": effect, "validation": src})
for d in diseases:
    done = set()
    for rid in sorted(dis_raw[d]):
        for t, r in raw_rows.get(rid, {}).items():
            if t in done:
                continue
            done.add(t)
            edge(d, "has_phenotype", t, "HPO annotations", rid, "https://hpo.jax.org/browse/term/" + t, r["evidence"], {"frequency": r["frequency"], "reference": r["reference"], "onset": r["onset"]})
for h in sorted(gene_paths):
    for p in sorted(gene_paths[h]):
        edge(h, "participates_in", "REACT:" + p, "Reactome", p, path_url[p], path_code[(h, p)], {})

tsv("nodes.tsv", ["id", "type", "name", "attributes"], nodes)
tsv("edges.tsv", ["edge_id", "subject", "predicate", "object", "source", "source_id", "source_url", "retrieved_date", "evidence_type", "evidence_code", "confidence", "quote", "contradicted_by", "attributes"], edges)
tsv("disease_classification.tsv", ["disease_id", "name", "genes", "mechanism_class", "phenotype_class", "direction", "n_pathways", "n_symptoms", "n_neighbors", "centrality"],
    [(d, name_of(d), "|".join(sorted(gene[g]["symbol"] for g in dis_genes[d])), mclass[d], pclass[d], direction[d], len(dis_paths[d]), len(dis_terms[d]), len(nbrs[d]), centrality[d]) for d in diseases])
nb_rows = []
for a, b, mech, pheno, same in sorted(scored, key=lambda x: -math.sqrt(x[2] * x[3])):
    sp, st = shared_evidence(a, b)
    nb_rows.append((a, b, round(mech, 3), round(pheno, 3), int(same), int(mclass[a] != mclass[b]), "|".join(p_name.get(p, p) for p in sp), "|".join(hp_name.get(t, t) for t in st)))
tsv("disease_neighbors.tsv", ["disease_a", "disease_b", "mechanism_similarity", "phenotype_similarity", "same_gene", "crosses_mechanism_class", "top_shared_pathways", "top_shared_symptoms"], nb_rows)

# ---------------------------------------------------------------- compact view
idx = {d: i for i, d in enumerate(diseases)}
mlist = [c for c, _ in Counter(mclass.values()).most_common()]
plist = [c for c, _ in Counter(pclass.values()).most_common()]
pth, trm = {}, {}


def pid(p):
    return pth.setdefault(p_name.get(p, p), len(pth))


def tid(t):
    return trm.setdefault(hp_name.get(t, t), len(trm))


view = {"mech": mlist, "pheno": plist, "d": [], "n": []}
for d in diseases:
    view["d"].append([d, name_of(d), mlist.index(mclass[d]), plist.index(pclass[d]), sorted(gene[g]["symbol"] for g in dis_genes[d])[:6],
                      direction[d], centrality[d], len(dis_terms[d]), len(dis_paths[d]), len(nbrs[d])])
    row = []
    for b, mech, pheno, same in nbrs[d][:TOP_NEIGHBORS]:
        sp, st = shared_evidence(d, b)
        row.append([idx[b], round(mech, 2), round(pheno, 2), int(same), [pid(p) for p in sp], [tid(t) for t in st]])
    view["n"].append(row)
view["paths"] = [k for k, _ in sorted(pth.items(), key=lambda x: x[1])]
view["terms"] = [k for k, _ in sorted(trm.items(), key=lambda x: x[1])]
with open(os.path.join(HERE, "atlas_view.json"), "w", encoding="utf-8") as f:
    json.dump(view, f, ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- report
print("genes in crosswalk", len(gene), "| disease genes", len(disease_genes_all))
print("diseases", len(diseases), "| mapped to MONDO", sum(d.startswith("MONDO") for d in diseases), "| gene-disease links kept", len(gd_rows), "skipped (non-causal or unmapped gene)", skipped)
print("with symptoms", sum(1 for d in diseases if dis_terms[d]), "| with pathway", n_with_path, "| with direction", sum(1 for d in diseases if direction[d]))
print("nodes", len(nodes), dict(Counter(n[1] for n in nodes)), "| edges", len(edges), dict(Counter(e[2] for e in edges)))
print("candidate pairs", len(pairs), "| neighbour pairs kept", len(scored), "| same-gene", sum(s[4] for s in scored), "| diseases with >=1 neighbour", sum(1 for d in diseases if nbrs[d]))
print("mechanism classes:", Counter(mclass.values()).most_common())
print("phenotype classes:", Counter(pclass.values()).most_common(12))
for q in ["MONDO:0012812"]:
    print("\ncheck", q, name_of(q), "|", mclass[q], "|", pclass[q], "| centrality", centrality[q])
    for b, mech, pheno, same in nbrs[q][:10]:
        print(f"   mech {mech:.2f} pheno {pheno:.2f} {'same gene' if same else '         '} {name_of(b)[:58]:58s} [{','.join(sorted(gene[g]['symbol'] for g in dis_genes[b]))[:20]}] {mclass[b]}")
