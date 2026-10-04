"""Step 7: merge every source into one slice graph and work out what it means for a patient group.

Outputs in data/slice/:
  nodes.tsv, edges.tsv   the merged graph, same columns as data/atlas, one source per edge
  slice_view.json        what the interface needs for the journey: search index, per-disease leads, bridges, gaps, evidence for every edge shown

Everything here is deterministic graph work; the model only phrases it afterwards (explain.py).
  - Mechanism per gene and disease: extracted paper claims first, then Orphanet, then the ClinVar variant spectrum.
    A gene is "contested" when papers support opposite mechanisms.
  - Bridges (network overlap): a researcher, organisation, funder, study or asset tied to two or more slice genes
    through at least two different papers, grants or studies (one paper naming two genes is not a bridge). A researcher also
    needs the same institution on two of those links, since people are matched by name.
  - Leads: each atlas neighbour of a disease, with the shared pathway, the mechanism comparison, the neighbour's community,
    the bridges the two share, and a verdict with its reasons. Opposite mechanisms make a counterexample, not a lead.
  - Gaps: for each disease, which sources were searched and came back empty, and the question that would close the gap.
"""
import json, math, os, re
from collections import Counter, defaultdict
from common import EDGE_COLS, SLICE, load_slice, read_tsv, write_tsv

PART_ORDER = ["atlas", "clinvar", "trials", "pubmed", "reporter", "orgs", "extract"]
sl = load_slice()
SEED = sl["seed"]
genes = {g["id"]: g for g in sl["genes"]}
sym2id = {g["symbol"]: g["id"] for g in sl["genes"]}
dis = {d["id"]: d for d in sl["diseases"]}

# ---------------------------------------------------------------- merge
nodes, edges, seen = {}, [], set()
for part in PART_ORDER:
    path = os.path.join(SLICE, "parts", part + "_nodes.tsv")
    if not os.path.exists(path):
        print("missing part:", part)
        continue
    for r in read_tsv(path):
        a = json.loads(r["attributes"])
        if r["id"] not in nodes:
            nodes[r["id"]] = {"id": r["id"], "type": r["type"], "name": r["name"], "attrs": a, "sources": [part]}
        else:
            n = nodes[r["id"]]
            n["sources"].append(part)
            if n["type"] == "researcher" and len(r["name"]) > len(n["name"]):
                n["name"] = r["name"]
            for k, v in a.items():
                n["attrs"].setdefault(k, v)
    for r in read_tsv(os.path.join(SLICE, "parts", part + "_edges.tsv")):
        key = (r["subject"], r["predicate"], r["object"], r["source_id"], r["quote"])
        if key not in seen:
            seen.add(key)
            edges.append(r)
E = {e["edge_id"]: e for e in edges}
attrs = lambda e: json.loads(e["attributes"])
out_by, in_by = defaultdict(list), defaultdict(list)
for e in edges:
    out_by[e["subject"]].append(e)
    in_by[e["object"]].append(e)
name = lambda i: nodes[i]["name"] if i in nodes else i

write_tsv(os.path.join(SLICE, "nodes.tsv"), ["id", "type", "name", "attributes"],
          [(n["id"], n["type"], n["name"], json.dumps({**n["attrs"], "found_in": n["sources"]}, ensure_ascii=False)) for n in sorted(nodes.values(), key=lambda n: n["id"])])
write_tsv(os.path.join(SLICE, "edges.tsv"), EDGE_COLS, [[e[c] for c in EDGE_COLS] for e in edges])

# ---------------------------------------------------------------- disease <-> gene, pathways
gene_dis, dis_gene = defaultdict(set), defaultdict(set)
for e in edges:
    if e["predicate"] == "gene_associated_with_condition":
        gene_dis[e["subject"]].add(e["object"])
        dis_gene[e["object"]].add(e["subject"])
gene_paths = defaultdict(dict)   # gene -> pathway -> edge id
for e in edges:
    if e["predicate"] == "participates_in":
        gene_paths[e["subject"]][e["object"]] = e["edge_id"]
path_size = {p: json.loads(json.dumps(nodes[p]["attrs"])).get("n_diseases", 999) for p in {p for d in gene_paths.values() for p in d}}

# ---------------------------------------------------------------- mechanism
MECH_WORD = {"loss_of_function": "loss of function", "gain_of_function": "gain of function", "dominant_negative": "dominant negative",
             "missense_driven": "missense-driven (direction not settled)"}
OPPOSITE = {frozenset(("loss_of_function", "gain_of_function")), frozenset(("loss_of_function", "dominant_negative")), frozenset(("gain_of_function", "dominant_negative"))}


def gene_mechanism(h):
    ev = []
    for e in out_by[h]:
        if e["predicate"] == "has_mechanism":
            ev.append(("paper", e["object"][5:], float(e["confidence"] or 0.5), e["edge_id"]))
        elif e["predicate"] == "mechanism_suggested_by_variant_spectrum":
            ev.append(("clinvar", e["object"][5:], float(e["confidence"] or 0.5), e["edge_id"]))
        elif e["predicate"] == "gene_associated_with_condition" and attrs(e).get("variant_effect"):
            ev.append(("orphanet", attrs(e)["variant_effect"].replace(" ", "_"), 0.8, e["edge_id"]))
    for tier in ("paper", "orphanet", "clinvar"):
        w = Counter()
        for t, m, c, _ in ev:
            if t == tier:
                w[m] += c
        if w:
            top, tw = w.most_common(1)[0]
            rivals = {m: v for m, v in w.items() if frozenset((m, top)) in OPPOSITE}
            contested = sum(rivals.values()) >= 0.3 * tw
            return {"label": top, "basis": tier, "contested": contested, "rivals": sorted(rivals), "weights": dict(w),
                    "evidence": [x[3] for x in ev], "n_paper_claims": sum(1 for x in ev if x[0] == "paper")}
    return {"label": "", "basis": "", "contested": False, "rivals": [], "weights": {}, "evidence": [], "n_paper_claims": 0}


gmech = {h: gene_mechanism(h) for h in genes}


specific = {d for d in dis if len(dis[d]["genes"]) <= 3}   # umbrella diseases list many genes; their labels say nothing about one gene
specific_of = {h: [d for d in gene_dis[h] if d in specific] for h in genes}


def gd_mechanism(h, d):
    """Mechanism of one gene in one disease. Levels: confirmed (paper or Orphanet on this gene-disease link),
    suggested (ClinVar spectrum or paper claims about the gene, used only when the gene causes just this one specific disease), or unknown."""
    claims, ids = Counter(), []
    for e in out_by[d]:
        if e["predicate"] == "caused_by_mechanism" and attrs(e).get("gene") == genes[h]["symbol"]:
            claims[e["object"][5:]] += float(e["confidence"] or 0.5)
            ids.append(e["edge_id"])
    if claims:
        return {"label": claims.most_common(1)[0][0], "level": "confirmed", "basis": "paper", "evidence": ids,
                "contested": len([m for m in claims if frozenset((m, claims.most_common(1)[0][0])) in OPPOSITE]) > 0}
    for e in in_by[d]:
        if e["predicate"] == "gene_associated_with_condition" and e["subject"] == h and attrs(e).get("variant_effect"):
            return {"label": attrs(e)["variant_effect"].replace(" ", "_"), "level": "confirmed", "basis": "orphanet", "evidence": [e["edge_id"]], "contested": False}
    m = gmech[h]
    if m["label"] and specific_of[h] == [d]:
        return {"label": m["label"], "level": "confirmed" if m["basis"] == "paper" else "suggested", "basis": "gene " + m["basis"],
                "evidence": m["evidence"], "contested": m["contested"]}
    why = f"{genes[h]['symbol']} causes {len(specific_of[h])} diseases here; its gene-level evidence is not applied to one of them" if m["label"] else ""
    return {"label": "", "level": "unknown", "basis": "", "evidence": [], "contested": False, "note": why}


def disease_mechanism(d):
    gs = [h for h in dis_gene[d] if h in genes]
    if d not in specific or not gs:
        return {"label": "", "level": "unknown", "basis": "", "evidence": [], "contested": False,
                "note": "umbrella disease with many genes; mechanism is judged per gene" if d not in specific else ""}
    ms = [gd_mechanism(h, d) for h in gs]
    ms.sort(key=lambda m: ["confirmed", "suggested", "unknown"].index(m["level"]))
    return ms[0]


dmech = {d: disease_mechanism(d) for d in dis}

# ---------------------------------------------------------------- communities: what is attached to each gene, and through which edge
PATIENT_PREDS = {"serves_community", "enrolls_gene", "runs_registry"}


def community(h):
    c = defaultdict(dict)   # kind -> node -> [edge ids]
    add = lambda kind, n, *eids: c[kind].setdefault(n, []).extend(eids)
    for e in in_by[h]:
        p, s = e["predicate"], e["subject"]
        if p in PATIENT_PREDS:
            add("patient_groups", s, e["edge_id"])
        elif p == "studies_gene":
            add("studies", s, e["edge_id"])
        elif p == "funds_research_on":
            add("grants", s, e["edge_id"])
        elif p == "mentions_gene":
            add("papers", s, e["edge_id"])
        elif p == "asset_for_gene":
            add("assets", s, e["edge_id"])
    for d in gene_dis[h]:
        for e in in_by[d]:
            if e["predicate"] == "studies_condition":
                add("studies", e["subject"], e["edge_id"])
    for org, eids in list(c["patient_groups"].items()):   # studies a patient group supports or co-funds
        for e in out_by[org]:
            if e["predicate"] in ("supports_study", "co_funds", "partners_with"):
                add("studies" if nodes[e["object"]]["type"] == "study" else "patient_groups", e["object"], *eids, e["edge_id"])
    for kind, lead_pred in (("papers", "authored"), ("grants", "leads_grant"), ("studies", "leads_study")):
        for n, eids in list(c[kind].items()):
            for e in in_by[n]:
                if e["predicate"] == lead_pred:
                    add("researchers", e["subject"], *eids, e["edge_id"])
    for n, eids in list(c["grants"].items()):
        for e in in_by[n]:
            if e["predicate"] == "funds":
                add("funders", e["subject"], *eids, e["edge_id"])
    for n, eids in list(c["studies"].items()):
        for e in in_by[n]:
            if e["predicate"] == "sponsors_study":
                add("sponsors", e["subject"], *eids, e["edge_id"])
    return {k: {n: sorted(set(v)) for n, v in d.items()} for k, d in c.items()}


comm = {h: community(h) for h in genes}

# ---------------------------------------------------------------- bridges: one node, two or more gene communities
touch = defaultdict(dict)   # node -> gene -> edge ids
for h, c in comm.items():
    for kind, items in c.items():
        if kind == "papers":
            continue   # a paper naming two genes is literature, not a shared asset; its authors still count
        for n, eids in items.items():
            touch[n][h] = eids
VIA = {"authored": "object", "leads_grant": "object", "leads_study": "object", "funds": "object", "sponsors_study": "object"}


def vias(eids):
    """The papers, grants or studies through which a node reaches a gene (or the edge itself when the link is direct)."""
    out = {E[i][VIA[E[i]["predicate"]]] for i in eids if E[i]["predicate"] in VIA}
    return out or set(eids)


GENERIC = set("university universit department dept hospital medical medicine center centre institute institut school college research clinical "
              "national children childrens health sciences science faculty division laboratory foundation general unit program the and for of "
              # fields and countries say little about whether two records are the same person
              "neuroscience neurosciences neurology neurological genetics genetic genomics genome molecular biology epilepsy pediatrics paediatrics "
              "pediatric paediatric psychiatry group kingdom united states america germany france italy denmark danish netherlands canada australia "
              "china japan spain sweden belgium switzerland england child from with".split())


def places(eids):
    """Institution words from the affiliations on a researcher's links (PubMed, RePORTER, ClinicalTrials.gov)."""
    out = set()
    for i in eids:
        for w in re.findall(r"[a-z]{4,}", (attrs(E[i]).get("affiliation") or "").lower()):
            if w not in GENERIC:
                out.add(w)
    return out


def shared_places(by_gene):
    ps = [places(v) for v in by_gene.values()]
    return sorted(set().union(*(ps[i] & ps[j] for i in range(len(ps)) for j in range(i + 1, len(ps)))))


def same_person(by_gene):
    """Names alone can merge two people; keep a researcher bridge only when two gene links share an institution word."""
    return bool(shared_places(by_gene))


bridges = []
for n, by_gene in touch.items():
    # one paper or study that names two genes is a single item, not a bridge between two communities
    if len(by_gene) >= 2 and len(set().union(*(vias(v) for v in by_gene.values()))) >= 2 and (nodes[n]["type"] != "researcher" or same_person(by_gene)):
        t = nodes[n]["type"]
        bridges.append({"node": n, "type": t, "genes": sorted(by_gene, key=lambda h: genes[h]["symbol"]), "edges": {genes[h]["symbol"]: v for h, v in by_gene.items()},
                        "identity_unverified": t == "researcher", "shared_institution": shared_places(by_gene)[:4] if t == "researcher" else []})
bridges.sort(key=lambda b: (-len(b["genes"]), b["type"], name(b["node"])))

# ---------------------------------------------------------------- leads: neighbours of each disease, judged
def shared_paths(a, b):
    out = []
    for ga in dis_gene[a] & set(genes):
        for gb in dis_gene[b] & set(genes):
            for p in set(gene_paths[ga]) & set(gene_paths[gb]):
                out.append((path_size.get(p, 999), p, ga, gb, gene_paths[ga][p], gene_paths[gb][p]))
    return sorted(out)[:3]


def lead(d, e):
    other = e["object"] if e["subject"] == d else e["subject"]
    a = attrs(e)
    sp = shared_paths(d, other)
    # compare the genes that carry the shared pathway, not whichever gene of a multi-gene disease has the most evidence
    m_a, m_b = (gd_mechanism(sp[0][2], d), gd_mechanism(sp[0][3], other)) if sp else (dmech[d], dmech[other])
    ma, mb = m_a["label"], m_b["label"]
    ga, gb = sorted(dis_gene[d] & set(genes)), sorted(dis_gene[other] & set(genes))
    shared = [b for b in bridges if set(ga) & set(b["genes"]) and set(gb) & set(b["genes"]) and not (set(ga) & set(gb))]
    neighbour_groups = sorted({n for h in gb for n in comm[h].get("patient_groups", {})})
    neighbour_studies = sorted({n for h in gb for n in comm[h].get("studies", {})})
    lv = [m_a["level"], m_b["level"]]
    strong_bridges = [b for b in shared if b["type"] in ("study", "researcher") or nodes[b["node"]]["attrs"].get("org_kind")]
    reasons = [f"mechanism similarity {a['mechanism_similarity']:.2f}, phenotype similarity {a['phenotype_similarity']:.2f}"]
    if sp:
        reasons.append("shared pathway: " + "; ".join(name(p[1]) for p in sp[:2]))
    if ma and mb and frozenset((ma, mb)) in OPPOSITE:
        treatment = "unlikely"
        reasons.append(f"opposite mechanisms: {MECH_WORD.get(ma, ma)} vs {MECH_WORD.get(mb, mb)}, so one treatment approach is unlikely to fit both")
    elif ma and ma == mb and "missense_driven" != ma:
        treatment = "likely" if lv == ["confirmed", "confirmed"] else "possible"
        reasons.append(f"both {MECH_WORD.get(ma, ma)}" + ("" if treatment == "likely" else " (at least one side only suggested by the variant spectrum)"))
    else:
        treatment = "unknown"
        unknown = [name(x) for x, m in ((d, ma), (other, mb)) if not m or m == "missense_driven"]
        reasons.append("mechanism not established for " + (" and ".join(unknown) if unknown else "both"))
    infrastructure = "yes" if a["phenotype_similarity"] >= 0.12 else "limited"
    reasons.append("overlapping symptoms, so registries, outcome measures and natural history data may transfer" if infrastructure == "yes"
                   else "little symptom overlap, so registries and outcome measures may not transfer")
    if strong_bridges:
        reasons.append(f"{len(strong_bridges)} shared studies, groups or researchers already connect the two communities")
    if a["same_gene"]:
        verdict = "same gene"
    elif treatment == "unlikely":
        verdict = "counterexample"
    elif a["mechanism_similarity"] >= 0.25 and infrastructure == "yes" and treatment == "likely" and (strong_bridges or neighbour_groups or neighbour_studies):
        verdict = "supported lead"
    elif (a["mechanism_similarity"] >= 0.25 and infrastructure == "yes") or strong_bridges:
        verdict = "plausible lead"
    else:
        verdict = "weak lead"
    rank = {"supported lead": 0, "plausible lead": 1, "same gene": 2, "counterexample": 3, "weak lead": 4}[verdict]
    path = [e["edge_id"]] + [x for p in sp[:1] for x in p[4:6]]
    path += [x["edge_id"] for h in ga for x in in_by[d] if x["subject"] == h and x["predicate"] == "gene_associated_with_condition"][:1]
    path += [x["edge_id"] for h in gb for x in in_by[other] if x["subject"] == h and x["predicate"] == "gene_associated_with_condition"][:1]
    return {"disease": other, "edge": e["edge_id"], "verdict": verdict, "rank": rank, "reasons": reasons, "path": path,
            "mechanism": [ma, mb], "mechanism_level": lv, "mechanism_evidence": m_a["evidence"] + m_b["evidence"],
            "via_genes": [sp[0][2], sp[0][3]] if sp else [], "treatment": treatment, "infrastructure": infrastructure, "shared_pathways": [p[1] for p in sp], "bridges": [b["node"] for b in shared],
            "neighbour_groups": neighbour_groups, "neighbour_studies": neighbour_studies,
            "score": round(math.sqrt(a["mechanism_similarity"] * a["phenotype_similarity"]), 3)}


leads = {}
for d in dis:
    ls = [lead(d, e) for e in out_by[d] + in_by[d] if e["predicate"] == "similar_mechanism_and_phenotype"]
    leads[d] = sorted(ls, key=lambda x: (x["rank"], -x["score"]))

# same gene, opposite mechanism: the brief's "same gene, different mechanisms" figure, found in the data
counterexamples = []
for h in genes:
    ms = {d: gd_mechanism(h, d) for d in gene_dis[h] if d in dis}
    ds = [d for d, m in ms.items() if m["level"] == "confirmed" and m["basis"] in ("paper", "orphanet")]
    for i, a in enumerate(ds):
        for b in ds[i + 1:]:
            if frozenset((ms[a]["label"], ms[b]["label"])) in OPPOSITE:
                counterexamples.append({"gene": h, "diseases": [a, b], "mechanisms": [ms[a]["label"], ms[b]["label"]],
                                        "evidence": ms[a]["evidence"] + ms[b]["evidence"]})

# ---------------------------------------------------------------- gaps: what was searched and found nothing
SOURCES = {"patient_groups": "patient organisation sites, NORD and Rare Epilepsy Network listings",
           "studies": "ClinicalTrials.gov", "grants": "NIH RePORTER (2021 onwards)", "papers": "PubMed", "assets": "models and assets read from PubMed abstracts"}


def gaps(d):
    gs = [h for h in dis_gene[d] if h in genes]
    out = []
    for kind, src in SOURCES.items():
        if not any(comm[h].get(kind) for h in gs):
            out.append({"missing": kind, "searched": src})
    if dmech[d]["level"] != "confirmed" or dmech[d]["label"] == "missense_driven":
        out.append({"missing": "mechanism", "searched": "Orphanet, ClinVar variant spectrum, PubMed claims"})
    if not leads[d]:
        out.append({"missing": "neighbours", "searched": "atlas: shared specific Reactome pathway plus overlapping HPO symptoms"})
    return out


# ---------------------------------------------------------------- view
SHOWN = {"disease", "gene", "pathway", "mechanism", "study", "organization", "researcher", "grant", "funder", "paper", "asset", "intervention"}
view_nodes = {}
for n in nodes.values():
    if n["type"] in SHOWN:
        a = {k: v for k, v in n["attrs"].items() if k in ("asset_type", "status", "phases", "study_type", "enrollment", "start", "conditions", "countries", "org_kind",
                                                        "org_class", "year", "journal", "is_review", "fiscal_years", "total_award", "activity_code", "is_active",
                                                        "asset_kind", "biospecimens", "n_locations", "primary_outcomes", "abbreviation", "intervention_type")}
        view_nodes[n["id"]] = {"t": n["type"], "n": n["name"], "a": a}
for d in dis.values():
    view_nodes[d["id"]]["a"] = {"genes": d["genes"], "synonyms": d["synonyms"][:12], "first_ring": d["in_first_ring"], "mechanism_class": d["mechanism_class"]}
for h, g in genes.items():
    view_nodes[h]["a"] = {"full_name": g["name"], "n_variants": sum(1 for e in in_by[h] if e["predicate"] == "variant_of")}

symptoms = defaultdict(list)
for d in dis:
    ts = sorted(((nodes[e["object"]]["attrs"].get("information_content", 0), e["object"]) for e in out_by[d] if e["predicate"] == "has_phenotype"), reverse=True)
    symptoms[d] = [nodes[t]["name"] for _, t in ts]
search = []
for d in dis.values():
    search.append([d["name"], d["id"], "disease"] + [[s for s in d["synonyms"]]])
for h, g in genes.items():
    search.append([g["symbol"], h, "gene", [g["name"]]])
for n in view_nodes:
    t = view_nodes[n]["t"]
    if t in ("organization", "mechanism", "pathway", "study", "intervention") and n not in dis:
        search.append([view_nodes[n]["n"], n, t, []])
sym_index = defaultdict(set)
for d, ts in symptoms.items():
    for t in ts:
        sym_index[t].add(d)
for t, ds in sym_index.items():
    search.append([t, "SYMPTOM:" + t, "symptom", sorted(ds)])

used = set()
for d in dis:
    for l in leads[d]:
        used.update(l["path"])
        used.add(l["edge"])
for h in genes:
    used.update(gmech[h]["evidence"])
    for kind, items in comm[h].items():
        for eids in items.values():
            used.update(eids)
for b in bridges:
    for v in b["edges"].values():
        used.update(v)
for d in dis:
    used.update(dmech[d]["evidence"])
for e in edges:
    if e["predicate"] in ("tests_intervention", "leads_study", "awarded_to", "describes_asset", "co_funds", "supports_study", "member_of", "partners_with",
                          "caused_by_mechanism", "has_mechanism"):
        used.add(e["edge_id"])
view_edges = {i: [E[i]["subject"], E[i]["predicate"], E[i]["object"], E[i]["source"], E[i]["source_id"], E[i]["source_url"], E[i]["retrieved_date"],
                  E[i]["evidence_type"], E[i]["evidence_code"], E[i]["confidence"], E[i]["quote"], E[i]["contradicted_by"],
                  {k: v for k, v in attrs(E[i]).items() if k in ("statement", "evidence_level", "disease_id", "mechanism_similarity", "phenotype_similarity",
                                                                "shared_pathways", "shared_symptoms", "n_pathogenic", "n_truncating", "n_missense",
                                                                "truncating_share", "rule", "role", "position", "affiliation", "variant_effect", "model", "same_gene")}]
              for i in sorted(used) if i in E}
for i, e in view_edges.items():
    for x in (e[0], e[2]):
        if x not in view_nodes and x in nodes:
            view_nodes[x] = {"t": nodes[x]["type"], "n": nodes[x]["name"], "a": {}}

coverage = {"sources": {p: len(read_tsv(os.path.join(SLICE, "parts", p + "_edges.tsv"))) for p in PART_ORDER if os.path.exists(os.path.join(SLICE, "parts", p + "_edges.tsv"))},
            "nodes": dict(Counter(n["type"] for n in nodes.values())), "edges": len(edges),
            "evidence_types": dict(Counter(e["evidence_type"] for e in edges))}
view = {"seed": SEED, "nodes": view_nodes, "edges": view_edges, "search": search, "coverage": coverage,
        "diseases": {d: {"mechanism": dmech[d], "leads": leads[d], "gaps": gaps(d), "symptoms": symptoms[d][:12], "n_symptoms": len(symptoms[d]),
                         "genes": sorted(dis_gene[d] & set(genes))} for d in dis},
        "genes": {h: {"mechanism": gmech[h], "community": comm[h]} for h in genes},
        "bridges": bridges, "counterexamples": counterexamples}
explain_path = os.path.join(SLICE, "explanations.json")
if os.path.exists(explain_path):
    with open(explain_path, encoding="utf-8") as f:
        view["explanations"] = json.load(f)
with open(os.path.join(SLICE, "slice_view.json"), "w", encoding="utf-8") as f:
    json.dump(view, f, ensure_ascii=False, separators=(",", ":"))

# ---------------------------------------------------------------- report
print("merged:", len(nodes), "nodes", coverage["nodes"], "|", len(edges), "edges", coverage["evidence_types"])
print("view:", len(view_nodes), "nodes,", len(view_edges), "edges,", round(os.path.getsize(os.path.join(SLICE, "slice_view.json")) / 1e6, 2), "MB")
for h in sorted(genes, key=lambda h: genes[h]["symbol"]):
    m = gmech[h]
    print(f"  {genes[h]['symbol']:8s} mechanism {MECH_WORD.get(m['label'], m['label'] or '?'):40s} from {m['basis'] or '-':8s} {'CONTESTED' if m['contested'] else ''}"
          f" | groups {len(comm[h].get('patient_groups', {}))} studies {len(comm[h].get('studies', {}))} grants {len(comm[h].get('grants', {}))} researchers {len(comm[h].get('researchers', {}))}")
print("bridges:", Counter(b["type"] for b in bridges))
for b in bridges[:12]:
    print(f"  {b['type']:12s} {name(b['node'])[:60]:60s} {[genes[h]['symbol'] for h in b['genes']]}")
print("counterexamples:", [(genes[c["gene"]]["symbol"], [name(x)[:40] for x in c["diseases"]], c["mechanisms"]) for c in counterexamples])
print(f"\nleads for the seed, {name(SEED)}:")
for l in leads[SEED]:
    print(f"  {l['verdict']:15s} {name(l['disease'])[:50]:50s} treat {l['treatment']:8s} infra {l['infrastructure']:7s} {'; '.join(l['reasons'][2:])[:120]}")
print("gaps for the seed:", [g["missing"] for g in gaps(SEED)])
