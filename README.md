# Raraction

Hack-Nation Challenge 05: AI Atlas for the World's Rare Diseases.

This branch (`yuzhu`) holds the first version of the atlas database: a cross-referenced knowledge graph of
7,999 monogenic rare diseases, built only from open structured sources, with each disease classified by
mechanism and by phenotype. Snapshot date: 2026-10-03. For research use only, not medical advice.

## What is here

| Path | Contents |
|---|---|
| [data/atlas/](data/atlas/) | The database: nodes, edges, crosswalk tables, classification, neighbour pairs, and the build script |
| [data/demo_graph/](data/demo_graph/) | A small ten-gene graph for trying things out |
| [views/atlas_cluster_view.html](views/atlas_cluster_view.html) | Searchable cluster view; download and open in a browser |
| [views/demo_graph.html](views/demo_graph.html) | Interactive view of the ten-gene graph |
| [scripts/download_raw.sh](scripts/download_raw.sh) | Downloads the raw source files (about 1 GB, not committed) |
| [data/README.md](data/README.md) | File-by-file reference: columns, keys, thresholds |

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
- **Search in the view covers disease names and gene symbols only.**

## Not built yet

- Mechanism links extracted from papers with a language model (the main gap: direction for the other 87%).
- Patient groups, registries, natural history studies, trials, researchers and funders.
- Variants from ClinVar.
- Finer mechanism clusters, using a middle pathway level or clustering on the neighbour graph.
- A single-file database (SQLite or DuckDB) with full-text search for the app.

## Sources

HPO, MONDO, Orphanet (Orphadata), Reactome and HGNC. Check and credit each source's licence terms when reusing
the data.
