"""Step 5: patient organisations, registries and shared studies, checked against the organisations' own pages.

data/slice/patient_orgs_seed.tsv lists candidate links found by hand search (NORD, Rare Epilepsy Network, organisation sites).
A candidate becomes an edge only when the page at its url, fetched now, has one sentence containing every term in its terms column;
that sentence is stored as the quote (a full sentence is preferred over a menu item or page title). Candidates that fail are reported and dropped, so the seed file can hold guesses safely.
"""
import html, os, re
from collections import Counter
from common import SLICE, Graph, cached, load_slice, read_tsv

sl = load_slice()
gene_id = {g["symbol"]: g["id"] for g in sl["genes"]}
ASSETS = {"ASSET:starr-study": ("STARR natural history study", "natural history study"),
          "ASSET:rare-x": ("RARE-X data collection program", "registry"),
          "ASSET:nyu-seizure-types-study": ("Observational study of seizure types in rare genetic epilepsies (NYU)", "observational study")}
ORG_NAMES = {"ORG:simons-searchlight": ("Simons Searchlight", "registry"), "ORG:european-stxbp1-consortium": ("European STXBP1 Consortium", "research consortium"),
             "ORG:combinedbrain": ("COMBINEDBrain", "consortium of patient organizations")}


def page_sentences(url):
    page, retrieved = cached("orgs", url.split("//")[-1], url, ok=lambda p: isinstance(p, str) and len(p) > 500, min_interval=1.0)
    text = re.sub(r"(?is)<!--.*?-->|<(script|style|noscript)\b.*?</\1>", " ", page)
    text = re.sub(r"(?i)<br\s*/?>|</(p|div|li|h\d|tr|td|section|article)>", ". ", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|\s*\.\s*\.\s*", text) if len(s.strip()) > 15], retrieved


g = Graph("orgs")
status = Counter()
for r in read_tsv(os.path.join(SLICE, "patient_orgs_seed.tsv")):
    terms = r["terms"].split("|")
    try:
        sentences, retrieved = page_sentences(r["url"])
    except Exception as ex:
        print(f"  unreachable  {r['url']}  ({str(ex)[:60]})")
        status["unreachable"] += 1
        continue
    hits = [s for s in sentences if all(t.lower() in s.lower() for t in terms)]
    full = [s for s in hits if 8 <= len(s.split()) <= 70]   # prefer a real sentence over a menu item or page title
    quote = (full or hits or [None])[0]
    if not quote:
        print(f"  not on page  {r['subject_name']} {r['predicate']} {r['object']}  {r['url']}")
        status["not found"] += 1
        continue
    status["verified"] += 1
    g.node(r["subject"], "researcher" if r["subject"].startswith("PERSON:") else "organization", r["subject_name"],
           **({} if r["subject"].startswith("PERSON:") else {"org_kind": r["subject_kind"]}))
    obj = gene_id.get(r["object"], r["object"])
    if obj in ASSETS:
        g.node(obj, "study", ASSETS[obj][0], asset_type=ASSETS[obj][1])
    elif obj in ORG_NAMES:
        g.node(obj, "organization", ORG_NAMES[obj][0], org_kind=ORG_NAMES[obj][1])
    g.edge(r["subject"], r["predicate"], obj, re.sub(r"^www\.", "", r["url"].split("/")[2]), r["url"], r["url"], retrieved, quote=quote[:400])
print(dict(status))
g.write()
