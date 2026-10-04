"""Step 3: PubMed papers on the mechanism of each slice gene, through NCBI E-utilities.

For each gene: the most relevant papers that name the gene next to a mechanism or model term, plus reviews, both limited to
nervous-system topics (the slice is neurological; this also stops GLS matching "global longitudinal strain").
A paper is kept for a gene only when its title or abstract names the symbol. All-letter symbols (GLS, CASK) also need the full
gene name, or a word such as "variant", "knockout" or "protein" right after the symbol. Paper and author nodes are observed facts. Abstracts go to data/slice/parts/pubmed_abstracts.json for the extraction step,
which reads claims out of them with a model. Only first and last authors are kept (usually the person doing the work and the lab head).
"""
import json, os, re
import xml.etree.ElementTree as ET
from common import SLICE, Graph, cached, load_slice, person_id, url

E = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
PER_GENE, REVIEWS = 25, 5
MECH = '(variant* OR mutation* OR haploinsufficien* OR "loss of function" OR "gain of function" OR "dominant negative" OR knockout OR "mouse model" OR "animal model" OR chaperone OR "gene therapy")'
DOMAIN = '(neuron* OR neural OR brain OR synap* OR epilep* OR seizure* OR encephalopath* OR neurodevelopment* OR "intellectual disability" OR dystonia OR ataxia OR hearing)'
sl = load_slice()
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


g = Graph("pubmed")
abstracts = {}
for gene in sl["genes"]:
    sym = gene["symbol"]
    pmids = []
    for label, term, n in [("mech", f"{sym}[tiab] AND {MECH} AND {DOMAIN}", PER_GENE), ("review", f"{sym}[tiab] AND review[pt] AND {DOMAIN}", REVIEWS)]:
        res, _ = cached("pubmed", f"{sym}-{label}", url(E + "esearch.fcgi", db="pubmed", term=term, retmax=n, sort="relevance", retmode="json"))
        pmids += [p for p in res["esearchresult"]["idlist"] if p not in pmids]
    if not pmids:
        continue
    xml, retrieved = cached("pubmed", f"{sym}-fetch", url(E + "efetch.fcgi", db="pubmed", id=",".join(pmids), retmode="xml"))
    for art in ET.fromstring(xml).iter("PubmedArticle"):
        pmid = art.findtext(".//MedlineCitation/PMID")
        a = art.find(".//Article")
        title = "".join(a.find("ArticleTitle").itertext()).strip()
        parts = []
        for t in a.findall(".//Abstract/AbstractText"):
            text = "".join(t.itertext()).strip()
            parts.append((t.get("Label") + ": " if t.get("Label") else "") + text)
        abstract = "\n".join(parts)
        text = title + ". " + abstract
        m = re.search(rf"[^.]*\b{sym}\b[^.]*\.?", text, re.I)
        if m and sym.isalpha():   # all-letter symbols collide with acronyms (GLS, "global longitudinal strain")
            m = (re.search(rf"[^.]*{re.escape(gene['name'])}[^.]*\.?", text, re.I)
                 or re.search(rf"[^.]*\b{sym}\b[- ]?(variant|mutation|mutant|gene|knock|deficien|related|haploinsufficien|protein|mRNA|expression|-/-|\+/-|mice)[^.]*\.?", text, re.I))
        if not m:   # [tiab] also searches author keywords
            continue
        year = art.findtext(".//JournalIssue/PubDate/Year") or (art.findtext(".//JournalIssue/PubDate/MedlineDate") or "")[:4]
        ptypes = [p.text for p in a.findall(".//PublicationType")]
        src = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        pid = "PMID:" + pmid
        g.node(pid, "paper", title, year=year, journal=a.findtext("Journal/ISOAbbreviation") or a.findtext("Journal/Title") or "",
               publication_types=ptypes, is_review="Review" in ptypes)
        abstracts[pmid] = {"title": title, "abstract": abstract, "year": year, "genes": sorted(set(abstracts.get(pmid, {}).get("genes", [])) | {sym})}
        g.edge(pid, "mentions_gene", gene["id"], "PubMed", pmid, src, retrieved, quote=m.group(0).strip()[:300])
        authors = [x for x in a.findall(".//AuthorList/Author") if x.findtext("LastName")]
        for pos, au in [("first author", authors[0]), ("last author", authors[-1])] if authors else []:
            per = person_id(au.findtext("LastName"), au.findtext("ForeName") or au.findtext("Initials") or "")
            if not per:
                continue
            name = f'{au.findtext("ForeName") or au.findtext("Initials") or ""} {au.findtext("LastName")}'.strip()
            aff = au.findtext(".//AffiliationInfo/Affiliation") or ""
            g.node(per, "researcher", name, identity="surname + first name; not verified across sources")
            g.edge(per, "authored", pid, "PubMed", pmid, src, retrieved, quote=name, position=pos, affiliation=aff[:300], year=year)
    print(f"  {sym:8s} {len(pmids)} found, {sum(1 for v in abstracts.values() if sym in v['genes'])} kept")
g.write()
with open(os.path.join(SLICE, "parts", "pubmed_abstracts.json"), "w", encoding="utf-8") as f:
    json.dump(abstracts, f, ensure_ascii=False, indent=0)
print("abstracts with text:", sum(1 for v in abstracts.values() if v["abstract"]), "of", len(abstracts))
