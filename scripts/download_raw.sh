#!/usr/bin/env bash
# Download the open source files the atlas is built from into data/raw (ignored by git, about 1 GB).
# Snapshot used for the committed outputs: 2026-10-03.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/raw/{mondo,hpo,clinvar,hgnc,orphanet,reactome,monarch}
cd data/raw
HPO=https://github.com/obophenotype/human-phenotype-ontology/releases/latest/download
curl -sSL --fail --retry 3 -Z \
  -o mondo/mondo.obo https://github.com/monarch-initiative/mondo/releases/latest/download/mondo.obo \
  -o hpo/hp.obo $HPO/hp.obo \
  -o hpo/phenotype.hpoa $HPO/phenotype.hpoa \
  -o hpo/genes_to_phenotype.txt $HPO/genes_to_phenotype.txt \
  -o hpo/genes_to_disease.txt $HPO/genes_to_disease.txt \
  -o clinvar/variant_summary.txt.gz https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz \
  -o clinvar/gene_condition_source_id https://ftp.ncbi.nlm.nih.gov/pub/clinvar/gene_condition_source_id \
  -o hgnc/hgnc_complete_set.txt https://storage.googleapis.com/public-download-files/hgnc/tsv/tsv/hgnc_complete_set.txt \
  -o orphanet/en_product6_genes.xml https://www.orphadata.com/data/xml/en_product6.xml \
  -o orphanet/en_product4_phenotypes.xml https://www.orphadata.com/data/xml/en_product4.xml \
  -o orphanet/en_product1_crossrefs.xml https://www.orphadata.com/data/xml/en_product1.xml \
  -o reactome/NCBI2Reactome.txt https://reactome.org/download/current/NCBI2Reactome.txt \
  -o reactome/ReactomePathways.txt https://reactome.org/download/current/ReactomePathways.txt \
  -o reactome/ReactomePathwaysRelation.txt https://reactome.org/download/current/ReactomePathwaysRelation.txt \
  -o monarch/monarch-kg.tar.gz https://data.monarchinitiative.org/monarch-kg/latest/monarch-kg.tar.gz
du -sh .
