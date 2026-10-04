# Raraction

Hack-Nation Challenge 05: AI Atlas for the World's Rare Diseases.

The repository has two layers:

- **The atlas**: a cross-referenced knowledge graph of 7,999 monogenic rare diseases, built only from open structured
  sources, with each disease classified by mechanism and by phenotype. Snapshot date: 2026-10-03.
- **The STXBP1 slice**: one complete journey from a diagnosis to a shared next step. It adds variants,
  studies, papers, grants, researchers and patient groups to the atlas around STXBP1 encephalopathy, and uses OpenAI models
  to read mechanism claims out of papers and to explain each connection in plain language.

For research use only, not medical advice.

## What is here

| Path | Contents |
|---|---|
| [data/atlas/](data/atlas/) | The database: nodes, edges, crosswalk tables, classification, neighbour pairs, and the build script |
| [data/demo_graph/](data/demo_graph/) | A small ten-gene graph for trying things out |
| [views/atlas_cluster_view.html](views/atlas_cluster_view.html) | **The user interface**: searchable cluster view of all 7,999 diseases, with the full journey for the STXBP1 slice. The map in the middle is a live force-directed graph, in the manner of Obsidian, of the selected disease, its genes, mechanism, shared pathways, neighbours and the groups, studies and people around them; drag a node and its neighbours follow, hover to light up its links, click any node or line for its source. Download and open in a browser |
| [views/demo_graph.html](views/demo_graph.html) | Interactive view of the ten-gene graph |
| [scripts/download_raw.sh](scripts/download_raw.sh) | Downloads the raw source files (about 1 GB, not committed) |
| [data/README.md](data/README.md) | File-by-file reference: columns, keys, thresholds |
| [pipeline/](pipeline/) | Scripts that build the slice, one per source, plus the merge, OpenAI and view steps; `build_view.py` writes the interface from `views/src/atlas.template.html` |
| [data/slice/](data/slice/) | The slice graph (`nodes.tsv`, `edges.tsv`), per-source parts, view data and cached model answers |
| [docs/05.pdf](docs/05.pdf) | The challenge brief |

## The STXBP1 slice

The brief asks for one complete journey: Maria types her disease, follows it to a disrupted pathway, another gene,
a related disease and the group working on it, finds a reusable asset, and leaves with a sourced next step, or with
an honest account of what is unknown. The slice builds that journey for STXBP1 encephalopathy (MONDO:0012812).

### Architecture

```
atlas (HPO, MONDO, Orphanet, Reactome, HGNC)
   │  slice.py        seed disease + its 12 atlas neighbours + every disease of their 12 core genes; MONDO synonyms from EBI OLS
   ├─ fetch_clinvar   pathogenic variants (NCBI E-utilities); variant spectrum -> inferred mechanism per gene
   ├─ fetch_trials    ClinicalTrials.gov API v2: registries, natural history studies, trials, sponsors, study leads
   ├─ fetch_pubmed    PubMed papers on each gene's mechanism, first and last authors
   ├─ fetch_reporter  NIH RePORTER grants, principal investigators, institutions, funding institutes
   ├─ fetch_orgs      patient groups and registries, each checked against the group's own web page
   ├─ extract_claims  OpenAI: mechanism claims and research assets read from abstracts (Extract + Reconcile)
   │  build_slice.py  merge; mechanism per gene-disease link; bridges; leads with verdicts; gaps
   ├─ explain         OpenAI: plain-language explanation, next step and draft message for each lead (Explain)
   │  build_view.py   embed atlas + slice data, a symptom index, atlas source links and force-graph into views/atlas_cluster_view.html
```

Every source writes `data/slice/parts/<source>_{nodes,edges}.tsv` in the atlas edge format (source, source id, url,
retrieved date, evidence type, confidence, quote, contradicted by). Raw API responses are cached in `data/slice/cache/`
so a rebuild runs offline; only the model answers are committed.

### Evidence rules

| Evidence type | Meaning | Guard |
|---|---|---|
| `observed` | Stated by a database, a registry entry or an organisation's own page | Gene links need the symbol in conditions or keywords, or next to a word such as "variant"; all-letter symbols (GLS, CASK) also need the full gene name, because "GLS" is also "global longitudinal strain". Patient groups are kept only when a sentence on their page, fetched by the script, contains the gene. |
| `extracted` | Read out of a PubMed abstract by an OpenAI model | The quote must appear word for word in the abstract; the disease id must come from the list offered; opposite mechanisms on one gene are linked through `contradicted_by` |
| `inferred` | Proposed by the graph | Atlas neighbour scores and the ClinVar variant spectrum; shown as proposals, never as facts |

Judgements made from the graph, before any model is involved:

- **Mechanism** is judged per gene and disease, not per gene, so two diseases of one gene can act in opposite directions
  (the brief's "same gene, different mechanisms"). Levels: confirmed (paper or Orphanet), suggested (variant spectrum), unknown.
- **A lead** answers two questions: can the two communities share infrastructure (overlapping symptoms), and could they
  share a treatment approach (same mechanism)? Opposite mechanisms make a counterexample, not a lead.
- **A bridge** (network overlap) is a researcher, group, funder or study tied to two genes through at least two different
  papers, grants or studies. Researchers are matched by surname and first name and also need the same institution on
  two of those links.
- **A gap** lists each source searched that came back empty for a disease, so "no result" is never silent.

### What the slice holds

| | Count |
|---|---|
| Genes / diseases | 12 / 42 |
| Pathogenic variants (ClinVar) | 1,263 |
| Studies (ClinicalTrials.gov and group pages) | 23 |
| Papers (PubMed) | 230 |
| NIH grants | 54 |
| Patient groups, registries and sponsors | 90 organisations, 29 links checked against live pages |
| Researchers | 440 |

### Rebuild the slice

```
python3 pipeline/slice.py            # needs data/atlas only
python3 pipeline/fetch_clinvar.py    # each fetch step caches its responses in data/slice/cache
python3 pipeline/fetch_trials.py
python3 pipeline/fetch_pubmed.py
python3 pipeline/fetch_reporter.py
python3 pipeline/fetch_orgs.py
python3 pipeline/extract_claims.py   # OpenAI; reuses committed answers, needs OPENAI_API_KEY only for new calls
python3 pipeline/build_slice.py
python3 pipeline/explain.py          # OpenAI, same caching
python3 pipeline/build_slice.py && python3 pipeline/build_view.py
```

Standard library only. Put `OPENAI_API_KEY=...` (and optionally `OPENAI_MODEL=...`) in a `.env` file at the repository
root, which git ignores.

## How the database was built

### 1. Download the open sources

| Source | Files | Used for |
|---|---|---|
| HPO | `phenotype.hpoa`, `genes_to_disease.txt`, `genes_to_phenotype.txt`, `hp.obo` | Disease to symptom, gene to disease, symptom hierarchy |
| MONDO | `mondo.obo` | Disease identifiers and cross-references |
| Orphanet | gene, phenotype and cross-reference files | Gene association type, including loss or gain of function where stated |
| Reactome | gene-to-pathway file and pathway hierarchy | Gene to pathway, pathway groups |
| HGNC | `hgnc_complete_set.txt` | Gene identifiers and aliases |

ClinVar and the Monarch knowledge graph are also downloaded but not yet used in the outputs.
OMIM is left out because it needs registration; HPO and Orphanet already carry its gene and disease links.

### 2. Check that the sources share keys

The sources have no single common column, but they join on two keys:

- **Disease:** MONDO identifier, reached from OMIM, Orphanet or GARD identifiers through MONDO's cross-references.
- **Gene:** HGNC identifier, reached from the NCBI gene number or symbol through the HGNC file.

Measured overlap: 12,754 of 12,880 HPO diseases map to MONDO, and of 5,283 HPO disease genes, 5,276 are in HGNC
and 4,024 have a Reactome pathway.

Two details matter when joining:

- Identifier formats differ between files (`NCBIGene:6812` and `6812`, `ORPHA:` and `Orphanet:`), so prefixes are normalised first.
- Only cross-references marked as exact are used to merge diseases.

### 3. Build the crosswalk tables

`crosswalk_genes.tsv` and `crosswalk_diseases.tsv` are the translation tables every other join goes through.

### 4. Build the graph

| | Count |
|---|---|
| Diseases | 7,999 |
| Genes | 5,090 |
| Symptoms | 10,291 |
| Pathways | 2,170 |
| Links | 216,503 |

- Links are gene to disease (13,883), disease to symptom (183,301) and gene to pathway (19,319).
- Only causal gene-to-disease links are kept: OMIM Mendelian, or Orphanet "disease-causing germline mutation".
  2,216 susceptibility, modifier and similar links were dropped.
- Every link records its source, source record, link, retrieval date and evidence code.
- All links are database facts (`evidence_type` = `observed`). The columns `confidence`, `quote` and
  `contradicted_by` are reserved for links extracted from papers.

### 5. Classify each disease on two axes

- **Mechanism cluster:** the top-level Reactome group of the causal gene's pathways (28 clusters).
- **Phenotype group:** the HPO organ system that carries most of the disease's specific symptoms.
- **Direction:** loss or gain of function, taken from Orphanet where stated.

### 6. Find neighbours

Two diseases are neighbours when their genes share a specific pathway and their symptoms overlap.
The two scores are kept separate:

- **Mechanism similarity:** overlap of pathway sets, with rare pathways weighted higher.
- **Phenotype similarity:** overlap of symptom sets including parent terms, with specific symptoms weighted higher.

This gives 15,929 neighbour pairs, 12,592 of them between different genes. Each pair lists its top shared
pathways and symptoms.

## Checked on the brief's STXBP1 example

| Method | Result |
|---|---|
| Search by name | One disease with "STXBP1" in its name |
| Symptoms only | The 15 nearest diseases are other epileptic encephalopathies with unrelated genes; 1 of 15 shares a pathway |
| Pathway and symptoms together | Neighbours are the synaptic vesicle release genes: CPLX1, SYT1, VAMP2 and others, under unrelated disease names |

So the joined graph reproduces the brief's central point: symptoms alone return lookalikes, and the pathway link
finds related diseases that a name search would miss.

## Rebuild

```
scripts/download_raw.sh                 # about 1 GB into data/raw (git-ignored)
python3 data/atlas/build_atlas.py       # standard library only, runs in seconds
python3 data/demo_graph/build_demo_graph.py
```

## Known limits

- **Mechanism cluster labels are coarse and sometimes wrong.** A disease gets one top-level group from very few
  pathways, so lysosomal storage diseases end up split across clusters. The neighbour scores are more reliable
  than the labels.
- **Direction is sparse.** Loss or gain of function is known for 1,067 diseases (13%).
- **Coverage gaps.** 1,491 diseases have no pathway, 791 have no symptoms, and 3,640 have no neighbour passing
  both thresholds.
- **332 diseases have no exact MONDO mapping** and may include duplicates.
- **Search covers disease names, genes and symptoms across the atlas**, but synonyms, patient groups, pathways,
  studies and drugs only within the slice (MONDO synonyms are not in the committed atlas files).
- **Slice: patient groups come from a hand-built seed list** (`data/slice/patient_orgs_seed.tsv`), checked against live
  pages but not exhaustive; NORD and Orphanet have no open API for their directories.
- **Slice: researchers are matched by name and institution words**, which can still merge or split people.
- **Slice: papers are read from abstracts only**, and NIH RePORTER covers US federal funding only.

## Not built yet

- Patient groups, trials, researchers and literature claims beyond the STXBP1 slice.
- Finer mechanism clusters for the whole atlas, using a middle pathway level or clustering on the neighbour graph.
- A single-file database (SQLite or DuckDB) with full-text search for the app.
- The 10× case: the existing timeline for a shared natural history study compared with the route the slice suggests.

## Sources

HPO, MONDO, Orphanet (Orphadata), Reactome and HGNC for the atlas; for the slice also ClinVar, ClinicalTrials.gov,
PubMed, NIH RePORTER, EBI OLS and the patient organisations' own pages. Check and credit each source's licence terms when reusing
the data.
