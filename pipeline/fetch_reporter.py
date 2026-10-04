"""Step 4: NIH-funded projects on the slice genes, from the NIH RePORTER API (fiscal years 2021 onwards).

Fiscal-year records are grouped by core project number. A project links to a gene when its title or abstract names the symbol next to a word such as "variant" or "related",
or names both the symbol and the gene's full name (this keeps acronyms such as an asthma study called CASK out).
Principal investigators, institutions and the funding institute become nodes, so a shared funder or lab can bridge two communities.
"""
import re
from collections import defaultdict
from common import Graph, cached, load_slice, person_id

API = "https://api.reporter.nih.gov/v2/projects/search"
YEARS = list(range(2021, 2027))
sl = load_slice()
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()

projects = defaultdict(list)
for gene in sl["genes"]:
    sym, offset = gene["symbol"], 0
    while True:
        body = {"criteria": {"fiscal_years": YEARS, "advanced_text_search": {"operator": "and", "search_field": "projecttitle,abstracttext", "search_text": sym}},
                "limit": 500, "offset": offset}
        res, retrieved = cached("reporter", f"{sym}-{offset}", API, data=body, min_interval=1.0)
        for p in res.get("results", []):
            projects[p["core_project_num"] or p["project_num"]].append((p, retrieved))
        offset += 500
        if offset >= res["meta"]["total"]:
            break

g = Graph("reporter")
kept = 0
for core, recs in sorted(projects.items()):
    recs.sort(key=lambda x: x[0]["fiscal_year"])
    p, retrieved = recs[-1]
    title, abstract = p.get("project_title") or "", p.get("abstract_text") or ""
    hits = []
    for gene in sl["genes"]:
        sym = gene["symbol"]
        text = title + ".\n" + abstract
        m = re.search(rf"[^.\n]{{0,100}}\b{sym}\b[- ]?(related|variant|mutation|gene|deficien|encephalopathy|disorder|knock)[^.\n]{{0,100}}", text, re.I)
        if not m and gene["name"].lower() in text.lower():
            m = re.search(rf"[^.\n]{{0,100}}\b{sym}\b[^.\n]{{0,100}}", text)
        m = m and m.group(0)
        if m:
            hits.append((gene, m.strip()))
    if not hits:
        continue
    kept += 1
    gid, src = "GRANT:" + core, p["project_detail_url"]
    years = sorted({r["fiscal_year"] for r, _ in recs})
    g.node(gid, "grant", title, activity_code=p.get("activity_code", ""), fiscal_years=years, is_active=p.get("is_active"),
           total_award=sum(r.get("award_amount") or 0 for r, _ in recs), start=(p.get("project_start_date") or "")[:10], end=(p.get("project_end_date") or "")[:10],
           abstract=abstract)
    for gene, quote in hits:
        g.edge(gid, "funds_research_on", gene["id"], "NIH RePORTER", p["project_num"], src, retrieved, quote=quote[:300])
    ic = p.get("agency_ic_admin") or {}
    if ic.get("abbreviation"):
        fid = "FUNDER:" + ic["abbreviation"]
        g.node(fid, "funder", ic.get("name") or ic["abbreviation"], abbreviation=ic["abbreviation"])
        g.edge(fid, "funds", gid, "NIH RePORTER", p["project_num"], src, retrieved, quote=ic.get("name", ""))
    org = (p.get("organization") or {}).get("org_name")
    if org:
        oid = "ORG:" + norm(org).replace(" ", "-")[:60]
        g.node(oid, "organization", org.title(), city=(p["organization"].get("org_city") or "").title(), country=(p["organization"].get("org_country") or "").title())
        g.edge(gid, "awarded_to", oid, "NIH RePORTER", p["project_num"], src, retrieved, quote=org)
    for pi in p.get("principal_investigators") or []:
        if person_id(pi.get("last_name"), pi.get("first_name")):
            per = person_id(pi["last_name"], pi["first_name"])
            name = f'{pi["first_name"].strip().title()} {pi["last_name"].strip().title()}'
            g.node(per, "researcher", name, identity="surname + first name; not verified across sources")
            g.edge(per, "leads_grant", gid, "NIH RePORTER", p["project_num"], src, retrieved, quote=pi.get("full_name", ""), contact_pi=pi.get("is_contact_pi"),
                   affiliation=org or "")
print("core projects seen", len(projects), "| kept", kept)
g.write()
