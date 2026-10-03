# Atlas database demo

A cross-referenced knowledge graph of monogenic rare diseases, built only from open structured sources.
Snapshot date: 2026-10-03. For research use only, not medical advice.

## Contents

| Path | What it is |
|---|---|
| `atlas/nodes.tsv` | 25,550 nodes: 7,999 diseases, 5,090 genes, 10,291 symptoms, 2,170 pathways |
| `atlas/edges.tsv.gz` | 216,503 links (gene to disease, disease to symptom, gene to pathway), 14 columns, one source per link |
| `atlas/crosswalk_genes.tsv` | Gene translation table: HGNC id, symbol, NCBI gene number, Ensembl, OMIM, aliases |
| `atlas/crosswalk_diseases.tsv` | Disease translation table: MONDO id with exact OMIM, Orphanet and GARD ids |
| `atlas/disease_classification.tsv` | Per disease: mechanism cluster, phenotype group, direction, centrality |
| `atlas/disease_neighbors.tsv` | 15,929 disease pairs sharing a specific pathway, with separate mechanism and phenotype scores |
| `atlas/atlas_view.json` | Compact copy used by the cluster view |
| `demo_graph/` | Small ten-gene graph (SYT1, STXBP1, STX1B, SYNGAP1, SCN1A, SCN2A, SCN3A, SCN8A, KCNQ2, KCNQ3) |
| `../views/atlas_cluster_view.html` | Searchable cluster view; open in a browser (loads fonts from Google Fonts) |
| `../views/demo_graph.html` | Interactive ten-gene graph; loads Cytoscape.js from cdnjs |

## Rebuild

```
scripts/download_raw.sh                 # about 1 GB into data/raw (git-ignored)
python3 data/atlas/build_atlas.py       # standard library only, a few seconds; writes edges.tsv uncompressed
python3 data/demo_graph/build_demo_graph.py
```

## Keys

Diseases are keyed by MONDO id (OMIM or Orphanet id where no exact MONDO mapping exists), genes by HGNC id,
symptoms by HPO term, pathways by Reactome id prefixed `REACT:`.

## Edge columns

`edge_id, subject, predicate, object, source, source_id, source_url, retrieved_date, evidence_type, evidence_code,
confidence, quote, contradicted_by, attributes`

Every link here comes from a database, so `evidence_type` is always `observed` and `confidence`, `quote` and
`contradicted_by` are empty. They are reserved for links extracted from papers.

## How diseases are classified

- Mechanism cluster: the top-level Reactome group of the causal gene's pathways.
- Phenotype group: the HPO organ system carrying most of the disease's specific symptoms.
- Neighbours: pairs whose genes share a pathway covering at most 60 diseases, scored separately on pathway overlap
  and symptom overlap (both weighted towards rare items), kept when both scores are at least 0.10.
- Only causal gene-to-disease links are kept (OMIM Mendelian, or Orphanet "disease-causing germline mutation").

## Known limits

- Mechanism cluster labels are coarse and sometimes wrong (lysosomal storage diseases are split across clusters).
  The pairwise neighbour scores are more reliable than the labels.
- Loss or gain of function is known for 1,067 diseases (13%), from Orphanet only.
- 1,491 diseases have no pathway, 791 have no symptoms, 3,640 have no neighbour passing both thresholds.
- 332 diseases have no exact MONDO mapping and may include duplicates.
- No patient groups, registries, trials, researchers or literature-extracted links yet.

## Sources

HPO annotations and ontology, MONDO, Orphanet (Orphadata products 1, 4 and 6), Reactome, HGNC.
ClinVar and the Monarch knowledge graph are downloaded by the script but not used in these outputs.
Check and credit each source's licence terms before redistribution.
