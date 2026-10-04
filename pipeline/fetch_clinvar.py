"""Step 1: pathogenic and likely pathogenic ClinVar variants for the slice genes, through NCBI E-utilities.

Variant nodes link to their gene, and to a disease only when ClinVar names the condition by a MONDO or OMIM id that maps exactly.
Variants spanning several genes are left out. The variant spectrum also gives one inferred mechanism edge per gene:
when most pathogenic variants truncate the protein, loss of function is the simplest explanation.
"""
import os
from collections import Counter
from common import ATLAS, Graph, cached, load_slice, read_tsv, url

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TRUNCATING = {"nonsense", "frameshift variant", "splice donor variant", "splice acceptor variant", "initiator codon variant", "start lost"}
MIN_VARIANTS = 10   # fewer than this is too thin to say anything about mechanism

sl = load_slice()
slice_dis = {d["id"] for d in sl["diseases"]}
omim2mondo = {}
for r in read_tsv(os.path.join(ATLAS, "crosswalk_diseases.tsv")):
    for o in filter(None, r["omim_ids"].split("|")):
        omim2mondo.setdefault(o, r["mondo_id"])


def to_disease(xrefs):
    for x in xrefs:
        db, i = x.get("db_source", ""), x.get("db_id", "")
        if db == "MONDO":
            d = i if i.startswith("MONDO:") else "MONDO:" + i
        elif db == "OMIM":
            d = omim2mondo.get("OMIM:" + i)
        else:
            continue
        if d in slice_dis:
            return d
    return None


def summaries(sym, ids, size=100):
    """Yield (record, uid, retrieved); halve the batch when NCBI refuses an oversized response (large multi-gene CNVs)."""
    for i in range(0, len(ids), size):
        batch = ids[i:i + size]
        try:
            summ, retrieved = cached("clinvar", f"{sym}-summary-{batch[0]}-{len(batch)}", url(E + "esummary.fcgi", db="clinvar", id=",".join(batch), retmode="json"),
                                     ok=lambda p: isinstance(p, dict) and "result" in p)
        except ValueError:
            if len(batch) == 1:
                print("    skipped oversized record", batch[0])
                continue
            yield from summaries(sym, batch, max(1, size // 4))
            continue
        for uid in summ["result"]["uids"]:
            yield summ["result"][uid], uid, retrieved


g = Graph("clinvar")
for gene in sl["genes"]:
    sym = gene["symbol"]
    term = f"{sym}[gene] AND (clinsig_pathogenic[prop] OR clinsig_likely_pathogenic[prop])"
    res, _ = cached("clinvar", sym + "-search", url(E + "esearch.fcgi", db="clinvar", term=term, retmax=5000, retmode="json"))
    ids = res["esearchresult"]["idlist"]
    spectrum, per_disease = Counter(), Counter()
    for v, uid, retrieved in summaries(sym, ids):
            if len({x["symbol"] for x in v.get("genes", [])}) != 1:
                continue
            cls = v["germline_classification"]
            cons = v.get("molecular_consequence_list") or []
            kind = "truncating" if TRUNCATING & set(cons) else "missense" if "missense variant" in cons else "other"
            spectrum[kind] += 1
            vid = "ClinVar:" + v["accession"]
            src = "https://www.ncbi.nlm.nih.gov/clinvar/variation/" + uid
            g.node(vid, "variant", v["title"], consequence=cons, protein_change=v.get("protein_change", ""), classification=cls["description"])
            g.edge(vid, "variant_of", gene["id"], "ClinVar", v["accession"], src, retrieved, code=cls["review_status"])
            for t in cls.get("trait_set", []):
                d = to_disease(t.get("trait_xrefs", []))
                if d:
                    per_disease[d] += 1
                    g.edge(vid, "causes_condition", d, "ClinVar", v["accession"], src, retrieved, code=cls["review_status"],
                           classification=cls["description"], trait_name=t.get("trait_name", ""), consequence=kind)
    n = sum(spectrum.values())
    g.node(gene["id"], "gene", sym)
    if n >= MIN_VARIANTS:
        share = spectrum["truncating"] / n
        mech = "MECH:loss_of_function" if share >= 0.3 else "MECH:missense_driven"
        g.node("MECH:loss_of_function", "mechanism", "loss of function (protein missing or reduced)")
        g.node("MECH:missense_driven", "mechanism", "missense-driven (altered protein: gain of function or dominant negative possible)")
        g.edge(gene["id"], "mechanism_suggested_by_variant_spectrum", mech, "ClinVar variant spectrum", f"{sym}[gene] P/LP",
               "https://www.ncbi.nlm.nih.gov/clinvar/?term=" + sym + "%5Bgene%5D", retrieved, "inferred", "truncating share",
               confidence=min(0.9, 0.5 + abs(share - 0.3)), n_pathogenic=n, n_truncating=spectrum["truncating"], n_missense=spectrum["missense"],
               truncating_share=round(share, 2), rule="truncating share >= 0.30 suggests loss of function; below that, missense variants dominate and the mechanism needs papers")
    print(f"  {sym:8s} {len(ids):5d} P/LP ids, {n:5d} single-gene, spectrum {dict(spectrum)}, mapped to slice diseases {dict(per_disease)}")
g.write()
