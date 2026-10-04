"""Step 8 (OpenAI): turn the leads and gaps that build_slice.py found into plain language a family can act on.

The model gets one lead at a time: the verdict and reasons computed from the graph, and the edges behind them (id, relation,
source, evidence type, confidence, quote). It may only use those edges. Every sentence it writes must cite edge ids from that list;
the script drops sentences whose ids are missing or invented. For a disease with gaps, it gets the search coverage and writes
what is unknown and the next question to test. Writes data/slice/explanations.json; run build_slice.py again to include it in the view.
"""
import json, os, sys
from common import SLICE, obj, openai_json

with open(os.path.join(SLICE, "slice_view.json"), encoding="utf-8") as f:
    V = json.load(f)
N, E, SEED = V["nodes"], V["edges"], V["seed"]
name = lambda i: N.get(i, {}).get("n", i)
cited = lambda: {"type": "array", "items": obj(text={"type": "string"}, edge_ids={"type": "array", "items": {"type": "string"}})}
LEAD_SCHEMA = obj(headline={"type": "string"}, for_family=cited(), reusable=cited(), differs=cited(),
                  expert_questions={"type": "array", "items": {"type": "string"}},
                  next_step=obj(action={"type": "string"}, who={"type": "string"}, edge_ids={"type": "array", "items": {"type": "string"}}),
                  proposal={"type": "string"})
GAP_SCHEMA = obj(summary={"type": "string"}, unknown={"type": "array", "items": {"type": "string"}}, next_question={"type": "string"},
                 how_to_help={"type": "string"})
SYSTEM = """You explain a rare-disease research graph to Maria, a parent who leads a patient group, and to the scientists she works with.
You receive one proposed connection between two diseases, a verdict already computed from the graph, and the evidence edges behind it.
Rules:
- Use only the edges given. Every item you write cites the edge ids it rests on; an item with no supporting edge must not be written.
- Separate what the data shows (evidence_type observed) from what was read out of papers (extracted) and what the graph proposes (inferred).
- Say plainly when something is uncertain or contradicted. Never promise a treatment.
- for_family: 3 to 5 short sentences, no jargon (explain pathway, loss of function and similar terms in everyday words).
- reusable: concrete assets (registries, natural history studies, trials, models, patient groups) the other community could reuse or join.
- differs: what is different between the two diseases or not yet known, which matters before joining forces.
- expert_questions: the biological or eligibility questions a clinician or scientist must check.
- next_step: one action Maria can take this week, and who to contact (an organisation or study named in the edges).
- proposal: a short message (under 120 words) Maria could send to that partner, citing the shared evidence in plain words.
Write in English."""
GAP_SYSTEM = """You explain to a parent what a rare-disease research graph does NOT know about their child's disease.
You receive the sources that were searched and came back empty, and what the graph does know. Be honest and specific:
say what is unknown, the single most useful next question to test, and how a patient group could help close the gap. Plain English, no jargon."""


def edge_line(i):
    s, p, o, src, sid, url, date, et, code, conf, quote, contra, a = E[i]
    line = f"[{i}] {name(s)} --{p}--> {name(o)} | source {src} {sid} | {et}" + (f", confidence {conf}" if conf else "")
    if quote:
        line += f' | quote: "{quote[:220]}"'
    if contra:
        line += f" | contradicted by {contra}"
    if a.get("statement"):
        line += f" | claim: {a['statement']}"
    return line


def lead_edges(d, l):
    ids = list(l["path"]) + l.get("mechanism_evidence", [])
    other = l["disease"]
    for b in l["bridges"]:
        for v in next(x for x in V["bridges"] if x["node"] == b)["edges"].values():
            ids += v
    for h in V["diseases"][other]["genes"]:
        c = V["genes"][h]["community"]
        for kind in ("patient_groups", "studies"):
            for n, eids in list(c.get(kind, {}).items())[:6]:
                ids += eids[:2]
    for h in V["diseases"][d]["genes"]:
        c = V["genes"][h]["community"]
        for n, eids in list(c.get("studies", {}).items())[:6]:
            ids += eids[:1]
    seen = []
    for i in ids:
        if i in E and i not in seen:
            seen.append(i)
    return seen[:60]


def keep_cited(items, allowed):
    out = []
    for it in items:
        ids = [i for i in it["edge_ids"] if i in allowed]
        if ids:
            out.append({"text": it["text"], "edge_ids": ids})
    return out


path = os.path.join(SLICE, "explanations.json")
result = {}
targets = [(SEED, l) for l in V["diseases"][SEED]["leads"]]
try:
    for d, l in targets:
        ids = lead_edges(d, l)
        user = (f"Maria's disease: {name(d)} (genes {', '.join(name(h) for h in V['diseases'][d]['genes'])})\n"
                f"Proposed connection: {name(l['disease'])} (genes {', '.join(name(h) for h in V['diseases'][l['disease']]['genes'])})\n"
                f"Verdict from the graph: {l['verdict']}. Shared treatment approach: {l['treatment']}. Shared infrastructure: {l['infrastructure']}.\n"
                f"Reasons: {'; '.join(l['reasons'])}\n\nEvidence edges:\n" + "\n".join(edge_line(i) for i in ids))
        out, retrieved, model = openai_json(f"explain-{d}-{l['disease']}", SYSTEM, user, "lead_explanation", LEAD_SCHEMA)
        allowed = set(ids)
        ns = out["next_step"]
        result[f"{d}|{l['disease']}"] = {"headline": out["headline"], "for_family": keep_cited(out["for_family"], allowed),
                                         "reusable": keep_cited(out["reusable"], allowed), "differs": keep_cited(out["differs"], allowed),
                                         "expert_questions": out["expert_questions"],
                                         "next_step": {**ns, "edge_ids": [i for i in ns["edge_ids"] if i in allowed]},
                                         "proposal": out["proposal"], "model": model, "retrieved": retrieved}
        r = result[f"{d}|{l['disease']}"]
        r["dropped_items"] = sum(len(out[k]) for k in ("for_family", "reusable", "differs")) - sum(len(r[k]) for k in ("for_family", "reusable", "differs"))
        print(f"  lead {name(l['disease'])[:50]:50s} {l['verdict']:15s} kept {sum(len(r[k]) for k in ('for_family', 'reusable', 'differs'))} cited items, dropped {r['dropped_items']}")
    for d, info in V["diseases"].items():
        if not N[d]["a"].get("first_ring") or not info["gaps"]:
            continue
        known = [f"{k}: {len(v)}" for h in info["genes"] for k, v in V["genes"][h]["community"].items()]
        user = (f"Disease: {name(d)} (genes {', '.join(name(h) for h in info['genes'])})\n"
                f"Mechanism: {info['mechanism']['label'] or 'not established'} ({info['mechanism']['level']})\n"
                f"Searched and found nothing: " + "; ".join(f"{g['missing']} (searched {g['searched']})" for g in info["gaps"]) +
                f"\nWhat the graph does have: {', '.join(known) or 'nothing beyond the gene and symptoms'}; {len(info['leads'])} neighbouring diseases"
                + (f", best: {name(info['leads'][0]['disease'])} ({info['leads'][0]['verdict']})" if info["leads"] else ""))
        out, retrieved, model = openai_json(f"gap-{d}", GAP_SYSTEM, user, "gap_explanation", GAP_SCHEMA)
        result[f"gap|{d}"] = {**out, "model": model, "retrieved": retrieved}
        print(f"  gap  {name(d)[:50]:50s} {[g['missing'] for g in info['gaps']]}")
except RuntimeError as ex:
    print("stopped:", ex)
with open(path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print("explanations:", len(result), "->", path)
if len(result) < len(targets):
    sys.exit(1)
