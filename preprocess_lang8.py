#!/usr/bin/env python
"""
Preprocessing script for Lang-8 v2 data. This script will:
1) Identify English sentence pairs (using langid.py),
2) Remove annotation tags (such as [f-blue], [f-red], and [sline]),
3) Retain only sentence pairs with modifications.
"""

import argparse
import json
import langid
import re
from functools import partial
from joblib import Parallel, delayed
from tqdm import tqdm


sline_pattern = re.compile(r'\[sline\].*?\[/sline\]')
color_tags = ['[f-blue]','[/f-blue]','[f-red]','[/f-red]','[f-bold]','[/f-bold]']
sent_end = ['.','?','!','"',"'"]


def remove_tags(line):
    for tag in color_tags:
        line = line.replace(tag, '')
    line = sline_pattern.sub('', line)
    line = line.replace('[/sline]', '')
    return re.sub('\s+', ' ', line)


def is_capitalized_sentence(line):
    return line[0] == line[0].upper() and line[-1] in sent_end


def process(line, is_aggresive=False):
    edited_pairs = set()
    unchanged_pairs = set()
    row = json.loads(re.sub(r'[\x00-\x1F]+', '', line))
    if row[2] == 'English':
        for i in range(len(row[4])):
            src_sent = row[4][i].strip()
            src_lang, _ = langid.classify(src_sent)
            if src_lang != 'en':
                continue
            src_sent = re.sub('\s+', ' ', src_sent)
            if len(row[5][i]) == 0: # no edits
                unchanged_pairs.add((src_sent, src_sent))
            for tgt_sent in row[5][i]:
                if not tgt_sent:
                    continue
                tgt_sent = tgt_sent.strip()
                tgt_sent = re.sub('\s+', ' ', tgt_sent)
                if tgt_sent == src_sent:
                    unchanged_pairs.append((src_sent, src_sent))
                    continue
                tgt_lang, _ = langid.classify(tgt_sent)
                if tgt_lang != 'en':
                    continue
                tgt_sent = remove_tags(tgt_sent).strip()
                if not tgt_sent:
                    # if it becomes empty after removing tags
                    continue
                if not is_aggresive or is_capitalized_sentence(tgt_sent):
                    edited_pairs.add((src_sent, tgt_sent))
    return edited_pairs, unchanged_pairs


def parallelize_preprocess(func, iterator, processes):
    """
    Adapted from https://github.com/alvations/sacremoses/blob/master/sacremoses/util.py#L213-L217.
    """
    iterator = tqdm(iterator)
    if processes <= 1:
        return map(func, iterator)
    return Parallel(n_jobs=processes)(delayed(func)(line) for line in iterator)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--data", required=True, help="The path to the data set")
    parser.add_argument("-o", "--output", required=True, help="Edited file prefix")
    parser.add_argument("-k", "--keep", required=True, help="Unchanged file prefix")
    parser.add_argument("-j", "--jobs", type=int, required=False, default=1, help="Number of parallel jobs")
    parser.add_argument("--aggresive", action="store_true", help="Aggresive filtering")
    args = parser.parse_args()

    with open(args.data) as fin, \
         open(args.output, 'w') as fout, \
         open(args.keep, 'w') as fkeep:

        process_func = partial(process, is_aggresive=args.aggresive)

        for edited_pairs, unchanged_pairs in parallelize_preprocess(
            process_func, fin.readlines(), args.jobs
        ):
            for src_sent, tgt_sent in edited_pairs:
                print("{}\t{}".format(src_sent, tgt_sent), end='\n', file=fout)
            for src_sent, tgt_sent in unchanged_pairs:
                print("{}\t{}".format(src_sent, tgt_sent), end='\n', file=fkeep)
