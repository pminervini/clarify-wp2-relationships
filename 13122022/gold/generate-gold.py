#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from tqdm import tqdm
import csv

from typing import Generator, Tuple, Dict, Set

import logging

logger = logging.getLogger(os.path.basename(sys.argv[0]))


def extract_names(mrconso_file: str,
                  en_only: bool = True,
                  lower_case: bool = True) -> Generator[Tuple[str, str], None, None]:
    """Reads UMLS concept names file MRCONSO.2019.RRF.

    Use ``en_only`` to read English concepts only.
    11743183 lines for UMLS2019.

    For details on each column, please check:
    https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.concept_names_and_sources_file_mr/?report=objectonly

    """
    with open(mrconso_file) as rf:
        for line in rf:
            line = line.strip()
            if not line:
                continue
            # Each line is as such:  C0000005|ENG|P|L0000005|PF|S0007492|Y|A26634265||M0019694|D012711|MSH|PEP|D012711|(131)I-Macroaggregated Albumin|0|N|256|
            line = line.split("|")
            # Consider en only
            if line[1] != "ENG" and en_only:
                continue
            e_id = line[0]
            e_text = line[-5].strip()
            if not e_text:
                continue
            if lower_case:
                e_text = e_text.lower()
            yield e_id, e_text
    return


def extract_types(mrsty_file: str) -> Generator[Tuple[str, str], None, None]:
    """Reads UMLS semantic types file MRSTY.2019.RRF.
    For details on each column, please check: https://www.ncbi.nlm.nih.gov/books/NBK9685/
    """
    with open(mrsty_file) as rf:
        for line in rf:
            line = line.strip()
            if not line:
                continue
            # Each line is as such:
            # 'C0000005|T116|A1.4.1.2.1.7|Amino Acid, Peptide, or Protein|AT17648347|256|
            # CUI|TUI|STN|STY|ATUI|CVF
            # Unique identifier of concept|Unique identifier of Semantic Type|Semantic Type tree number|Semantic Type. The valid values are defined in the Semantic Network.|Unique identifier for attribute|Content View Flag
            line = line.split("|")
            e_id = line[0]
            e_type = line[3].strip()
            # considering entities with entity types only
            if not e_type:
                continue
            yield e_id, e_type
    return


def extract_rels(mrrel_file: str,
                 ro_only: bool = True) -> Generator[Tuple[str, str, str], None, None]:
    """Reads UMLS relation triples file MRREL.2019.RRF.
    Use ``ro_only`` to consider relations of "RO" semantic type only.
    50813206 lines in UMLS2019.
    RO = has relationship other than synonymous, narrower, or broader
    For details on each column, please check:
    https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly
    """
    with open(mrrel_file) as rf:
        for line in rf:
            line = line.strip()
            if not line:
                continue

            # Each line is as such: C0012792|A24166664|SCUI|RO|C0026827|A0088733|SCUI|induced_by|R176819430||MED-RT|MED-RT||N|N||
            line = line.split("|")

            # Consider relations of 'RO' type only
            if line[3] != "RO" and ro_only:
                continue

            e1_id: str = line[0]
            e2_id: str = line[4]
            rel_text: str = line[7].strip()

            # considering relations with textual descriptions only
            if not rel_text:
                continue

            yield rel_text, e1_id, e2_id
    return


def extract_rels_wih_source(mrrel_file: str,
                            ro_only: bool = True,
                            rela_only: bool = True) -> Generator[Tuple[str, str, str, str, str, str, str], None, None]:
    """Reads UMLS relation triples file MRREL.2019.RRF.
    Use ``ro_only`` to consider relations of "RO" semantic type only.
    50813206 lines in UMLS2019.
    RO = has relationship other than synonymous, narrower, or broader
    For details on each column, please check:
    https://www.ncbi.nlm.nih.gov/books/NBK9685/table/ch03.T.related_concepts_file_mrrel_rrf/?report=objectonly
    """
    with open(mrrel_file) as rf:
        for line in rf:
            line = line.strip()
            if not line:
                continue

            # Each line is as such: C0012792|A24166664|SCUI|RO|C0026827|A0088733|SCUI|induced_by|R176819430||MED-RT|MED-RT||N|N||
            line = line.split("|")
            # print(line)

            # Consider relations of 'RO' type only
            if line[3] != "RO" and ro_only:
                continue

            e1_id: str = line[0].strip()
            e2_id: str = line[4].strip()
            # print(e1_id, e2_id)

            # RELA	Additional (more specific) relationship label (optional)
            rel_text: str = line[7].strip()
            rui_value: str = line[8].strip()

            srui_value: str = line[9].strip()
            sab_value: str = line[10].strip()
            sl_value: str = line[11].strip()

            # considering relations with textual descriptions only
            if (not rel_text) and rela_only:
                continue

            yield rel_text, e1_id, e2_id, rui_value, srui_value, sab_value, sl_value
    return


def main(argv):
    with open('umls_concepts_v2.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        adrianna_cui_set = {row[1] for i, row in enumerate(reader) if len(row[1]) > 0 and i > 0}

    print(adrianna_cui_set)

    mrconso_path = os.path.expanduser('~/workspace/aihn-ucsd/amil/data/UMLS/raw/MRCONSO.RRF')
    mrrel_path = os.path.expanduser('~/workspace/aihn-ucsd/amil/data/UMLS/raw/MRREL.RRF')
    mrsty_path = os.path.expanduser('~/workspace/aihn-ucsd/amil/data/UMLS/raw/MRSTY.RRF')

    cui_to_names: Dict[str, Set[str]] = dict()
    cui_to_types: Dict[str, Set[str]] = dict()
    adrianna_cui_triples: Set[Tuple[str, str, str]] = set()

    logger.info('Reading CUI names ..')

    for cui, name in tqdm(extract_names(mrconso_path)):
        if cui not in cui_to_names:
            cui_to_names[cui] = set()
        cui_to_names[cui] |= {name}

    with open('clarify_has_name_triples.tsv', 'wt') as f:
        writer = csv.writer(f, delimiter='\t')
        for cui in adrianna_cui_set:
            if cui in cui_to_names:
                for name in cui_to_names[cui]:
                    writer.writerow([cui, 'has_name', name])

    logger.info('Reading CUI types ..')

    for cui, cui_type in tqdm(extract_types(mrsty_path)):
        if cui not in cui_to_types:
            cui_to_types[cui] = set()
        cui_to_types[cui] |= {cui_type}

    with open('clarify_has_type_triples.tsv', 'wt') as f:
        writer = csv.writer(f, delimiter='\t')
        for cui in adrianna_cui_set:
            if cui in cui_to_types:
                for type in cui_to_types[cui]:
                    writer.writerow([cui, 'has_type', type])

    logger.info('Reading CUI triples with sources ..')

    for p, s, o, rui, srui, sab, sl in tqdm(extract_rels_wih_source(mrrel_path, ro_only=False, rela_only=False)):
        if s in adrianna_cui_set or o in adrianna_cui_set:
            adrianna_cui_triples |= {(s, o, p, rui, sl)}
            assert sab == sl

    with open('gold_triples_with_sources.tsv', 'wt') as f:
        writer = csv.writer(f, delimiter='\t')
        for s, o, p, rui, sl in adrianna_cui_triples:
            writer.writerow([s, o, p, rui, sl])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main(sys.argv[1:])
