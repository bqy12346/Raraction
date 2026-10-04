"""Step 2: studies from ClinicalTrials.gov (API v2) for the slice genes and the seed's neighbour diseases.

Each study becomes a node typed by what it can offer another community: registry, natural history study, interventional trial,
or other observational study. Asset type comes from structured fields (patientRegistry, studyType) and the title, not from a model.
Study officials and sponsors become researcher and organisation nodes; contact emails and phones are not copied.
A study links to a gene only when the symbol appears in its conditions or keywords, or next to a word such as "variant" or "related"
in its title or summary, and the record mentions genetics, epilepsy or the gene's full name anywhere, so that GLS
(also "global longitudinal strain") does not pull in cardiology trials.
"""
import re
from common import Graph, cached, load_slice, person_id, split_name, url

API = "https://clinicaltrials.gov/api/v2/studies"
PAGE = 100
sl = load_slice()
genes = {g["symbol"]: g["id"] for g in sl["genes"]}
full_name = {g["symbol"]: g["name"] for g in sl["genes"]}
GENETIC = r"\bgene\b|genetic|variant|mutation|pathogenic|de novo|encephalopath|epilep"
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()
dis_names = {}
for d in sl["diseases"]:
    for n in [d["name"]] + d["synonyms"]:
        if len(n) >= 6:
            dis_names.setdefault(norm(n), d["id"])


def org_id(name):
    return "ORG:" + norm(name).replace(" ", "-")[:60]


def queries():
    for sym in genes:
        yield sym, {"query.term": sym}
    for d in sl["diseases"]:
        if d["in_first_ring"]:
            for n in [d["name"]] + [s for s in d["synonyms"] if len(s) >= 6]:
                yield n, {"query.cond": f'"{n}"'}


studies = {}
for key, q in queries():
    token = None
    while True:
        res, retrieved = cached("ctgov", key, url(API, pageSize=PAGE, **q, **({"pageToken": token} if token else {})))
        for s in res.get("studies", []):
            studies.setdefault(s["protocolSection"]["identificationModule"]["nctId"], (s, retrieved))
        token = res.get("nextPageToken")
        if not token or len(studies) > 2000:
            break


def gene_hits(p):
    c = p.get("conditionsModule", {})
    tagged = " | ".join(c.get("conditions", []) + c.get("keywords", []))
    text = p["identificationModule"].get("officialTitle", "") + " " + p["identificationModule"]["briefTitle"] + " " + p.get("descriptionModule", {}).get("briefSummary", "")
    everything = tagged + " " + text + " " + p.get("descriptionModule", {}).get("detailedDescription", "")
    for sym in genes:
        if not (re.search(GENETIC, everything, re.I) or full_name[sym].lower() in everything.lower()):
            continue
        if re.search(rf"\b{sym}\b", tagged):
            yield sym, tagged
        else:
            m = re.search(rf"[^.]{{0,80}}\b{sym}\b[- ]?(related|variant|mutation|gene|deficien|encephalopathy|disorder)[^.]{{0,80}}", text, re.I)
            if m:
                yield sym, m.group(0).strip()


def asset_type(p):
    d = p.get("designModule", {})
    title = (p["identificationModule"]["briefTitle"] + " " + p["identificationModule"].get("officialTitle", "")).lower()
    if d.get("patientRegistry"):
        return "registry"
    if "natural history" in title:
        return "natural history study"
    if d.get("studyType") == "INTERVENTIONAL":
        return "interventional trial"
    return "observational study"


g = Graph("trials")
kept = 0
for nct, (s, retrieved) in sorted(studies.items()):
    p = s["protocolSection"]
    hits = list(gene_hits(p))
    conds = p.get("conditionsModule", {}).get("conditions", [])
    dis_hits = [(c, dis_names[norm(c)]) for c in conds if norm(c) in dis_names]
    if not hits and not dis_hits:
        continue
    kept += 1
    sid, src = "NCT:" + nct, "https://clinicaltrials.gov/study/" + nct
    st, d = p["statusModule"], p.get("designModule", {})
    g.node(sid, "study", p["identificationModule"]["briefTitle"], asset_type=asset_type(p), status=st.get("overallStatus", ""),
           phases=d.get("phases", []), study_type=d.get("studyType", ""), enrollment=d.get("enrollmentInfo", {}).get("count"),
           start=st.get("startDateStruct", {}).get("date", ""), completion=st.get("completionDateStruct", {}).get("date", ""),
           conditions=conds, biospecimens=d.get("bioSpec", {}).get("retention", ""), n_locations=len(p.get("contactsLocationsModule", {}).get("locations", [])),
           countries=sorted({l.get("country", "") for l in p.get("contactsLocationsModule", {}).get("locations", [])} - {""}),
           summary=p.get("descriptionModule", {}).get("briefSummary", ""), eligibility=p.get("eligibilityModule", {}).get("eligibilityCriteria", ""),
           primary_outcomes=[o.get("measure", "") for o in p.get("outcomesModule", {}).get("primaryOutcomes", [])])
    for sym, quote in hits:
        g.edge(sid, "studies_gene", genes[sym], "ClinicalTrials.gov", nct, src, retrieved, quote=quote[:300])
    for c, did in dis_hits:
        g.edge(sid, "studies_condition", did, "ClinicalTrials.gov", nct, src, retrieved, quote=c)
    for i in p.get("armsInterventionsModule", {}).get("interventions", []):
        iid = "INT:" + norm(i["name"]).replace(" ", "-")[:60]
        g.node(iid, "intervention", i["name"], intervention_type=i.get("type", ""))
        g.edge(sid, "tests_intervention", iid, "ClinicalTrials.gov", nct, src, retrieved, quote=i["name"])
    sp = p.get("sponsorCollaboratorsModule", {})
    for role, o in [("lead sponsor", sp.get("leadSponsor"))] + [("collaborator", c) for c in sp.get("collaborators", [])]:
        if o and o.get("name"):
            g.node(org_id(o["name"]), "organization", o["name"], org_class=o.get("class", ""))
            g.edge(org_id(o["name"]), "sponsors_study", sid, "ClinicalTrials.gov", nct, src, retrieved, quote=o["name"], role=role)
    for o in p.get("contactsLocationsModule", {}).get("overallOfficials", []):
        pid = person_id(*split_name(o.get("name", "")))
        if pid:
            g.node(pid, "researcher", o["name"], identity="surname + first name; not verified across sources")
            g.edge(pid, "leads_study", sid, "ClinicalTrials.gov", nct, src, retrieved, quote=f'{o["name"]}, {o.get("affiliation", "")}', role=o.get("role", ""),
                   affiliation=o.get("affiliation", ""))
            if o.get("affiliation"):
                g.node(org_id(o["affiliation"]), "organization", o["affiliation"])
                g.edge(pid, "affiliated_with", org_id(o["affiliation"]), "ClinicalTrials.gov", nct, src, retrieved, quote=o["affiliation"])
print("studies seen", len(studies), "| kept", kept)
g.write()
