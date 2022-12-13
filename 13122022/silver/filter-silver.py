#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import gzip
import json
import csv

from tqdm import tqdm

from typing import Set, Tuple

import logging

logger = logging.getLogger(os.path.basename(sys.argv[0]))


def main(argv):
    with open('umls_concepts_v2.csv', 'r') as f:
        reader = csv.reader(f, delimiter=',')
        adrianna_cui_set = {row[1] for i, row in enumerate(reader) if len(row[1]) > 0 and i > 0}

    path = '/Users/pasquale/workspace/meddistant-baselines/comp/predictions.large.jsonl.gz'

    adrianna_silver_triples: Set[Tuple[str, str, str]] = set()

    with gzip.open(path, 'r') as rf, open('silver_triples.tsv', 'wt') as wf:
        writer = csv.writer(wf, delimiter='\t')

        for line in tqdm(rf):
            obj = json.loads(line)

            add_triple = False
            for e in obj['entpair']:
                if e in adrianna_cui_set:
                    add_triple = True

            if add_triple is True:
                score_value = float(obj['score'])

                if score_value > 0.5:
                    s = obj['entpair'][0]
                    o = obj['entpair'][1]
                    p = obj['relation']

                    if (s, p, o) not in adrianna_silver_triples:
                        adrianna_silver_triples |= {(s, p, o)}
                        writer.writerow([s, p, o])


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    main(sys.argv[1:])
