# Gold Triples

The script `generate-gold.py` acquires a list of CUIs from `umls_concepts_v2.csv` (shared by Adrianna). Then, it goes through `MRREL.RRF` (its structure is outlined [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly)) in UMLS, and extracts the relationships that involve at least one of such CUIs. These are saved in `gold_triples_with_sources.tsv`, which contains the following fields:
- The subject of the relationship (`CUI1` in `MRREL.RRF`, see [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly)),
- The object of the relationship (`CUI2` in `MRREL.RRF`, see [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly)),
- Specific relationship label (optional -- `RELA` in `MRREL.RRF`, see [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly))
- Unique identifier of the relationship (`RUI` in `MRREL.RRF`, see [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly))
- Source of the relationship (`SL` in `MRREL.RRF`, see [here](https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly))

In addition, it generates the following files:
- `clarify_has_type_triples.tsv`, containing CUI type information from `MRSTY.RRF`, and
- `clarify_has_name_triples.tsv`, containing CUI names from `MRCONSO.RRF`
