#!/usr/bin/env python

'''
Preprocessing script for Lang-8 v2 data. This script will:
1) Identify English sentence pairs (using langid.py),
2) Remove annotation tags (such as [f-blue], [f-red], and [sline]),
3) Retain only sentence pairs with modifications.
'''

import codecs, json, re, sys, time
import multiprocessing
import langid

NUM_JOBS = 8
AGGRESIVE = False

SLINE_PATTERN = re.compile(r'\[sline\].*?\[/sline\]')

SENT_END = ['.','?','!','"',"'"]

def remove_tags(line):
    for tag in ['[f-blue]','[/f-blue]','[f-red]','[/f-red]','[f-bold]','[/f-bold]']:
        line = line.replace(tag, '')
    line = SLINE_PATTERN.sub('', line)
    line = line.replace('[/sline]', '')
    return re.sub('\s+', ' ', line)

def process(line):
    sentence_pairs = []
    unchanged_sentence_pairs = []
    row = json.loads(re.sub(r'[\x00-\x1F]+', '', line))
    if row[2] == 'English':
        for i in range(len(row[4])):
            src_sent = row[4][i].strip()
            src_lang, _ = langid.classify(src_sent)
            if src_lang != 'en':
                continue
            src_sent = re.sub('\s+', ' ', src_sent)
            has_added = False
            if len(row[5][i]) == 0:
                unchanged_sentence_pairs.append((src_sent, src_sent))
                has_added = True
            for tgt_sent in row[5][i]:
                if not tgt_sent:
                    continue
                tgt_sent = re.sub('\s+', ' ', tgt_sent)
                if tgt_sent.strip() == src_sent:
                    if not has_added:
                        unchanged_sentence_pairs.append((src_sent, src_sent))
                        has_added = True
                    continue
                tgt_lang, _ = langid.classify(tgt_sent)
                if tgt_lang != 'en':
                    continue
                tgt_sent = remove_tags(tgt_sent)
                tgt_sent = tgt_sent.strip()
                if tgt_sent and \
                   (not AGGRESIVE or \
                    (tgt_sent[0] == tgt_sent[0].upper() \
                    and tgt_sent[-1] in SENT_END)):
                    sentence_pairs.append((src_sent, tgt_sent))
    return sentence_pairs, unchanged_sentence_pairs

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print "usage: <raw input> <output> <keep> src tgt"
        sys.exit(1)

    print "Start processing"
    start_time = time.time()
    pool = multiprocessing.Pool(NUM_JOBS)
    results = [pool.apply_async(process, (line,)) for line in open(sys.argv[1])]
    src_fn = sys.argv[2]+'.'+sys.argv[4]
    tgt_fn = sys.argv[2]+'.'+sys.argv[5]
    src_keep_fn = sys.argv[3]+'.'+sys.argv[4]
    tgt_keep_fn = sys.argv[3]+'.'+sys.argv[5]
    with open(src_fn, 'w') as src_f, \
         open(tgt_fn, 'w') as tgt_f, \
         open(src_keep_fn, 'w') as src_keep_f, \
         open(tgt_keep_fn, 'w') as tgt_keep_f:
        for result in results:
            sentence_pairs, unchanged_sentence_pairs = result.get()
            for src_sent, tgt_sent in sentence_pairs:
                src_f.write(src_sent.encode('utf-8')+'\n')
                tgt_f.write(tgt_sent.encode('utf-8')+'\n')
            for src_sent, tgt_sent in unchanged_sentence_pairs:
                src_keep_f.write(src_sent.encode('utf-8')+'\n')
                tgt_keep_f.write(tgt_sent.encode('utf-8')+'\n')
    print "Done in", time.time()-start_time, "seconds"
    
