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

num_jobs = 8

sline_pattern = re.compile(r'\[sline\].*?\[/sline\]')

def remove_tags(line):
    for tag in ['[f-blue]','[/f-blue]','[f-red]','[/f-red]']:
        line = line.replace(tag, '')
    line = sline_pattern.sub('', line)
    line = line.replace('[/sline]', '')
    return re.sub('\s+', ' ', line)

def process(line):
    sentence_pairs = []
    row = json.loads(re.sub(r'[\x00-\x1F]+', '', line))
    if row[2] == 'English':
        for i in range(len(row[4])):
            src_sent = row[4][i]
            src_lang, _ = langid.classify(src_sent)
            if src_lang != 'en': continue
            for tgt_sent in row[5][i]:
                if not tgt_sent: continue
                if tgt_sent == src_sent: continue
                tgt_lang, _ = langid.classify(tgt_sent)
                if tgt_lang != 'en': continue
                src_sent = re.sub('\s+', ' ', src_sent)
                tgt_sent = remove_tags(tgt_sent)
                sentence_pairs.append((src_sent, tgt_sent))
    return sentence_pairs

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "usage: <raw input> <output.src> <output.tgt>"
        sys.exit(1)

    print "Start processing"
    start_time = time.time()
    pool = multiprocessing.Pool(num_jobs)
    results = [pool.apply_async(process, (line,)) for line in open(sys.argv[1])]
    with open(sys.argv[2], 'w') as src_f, \
         open(sys.argv[3], 'w') as tgt_f:
        for sentence_pairs in results:
            for src_sent, tgt_sent in sentence_pairs.get():
                src_f.write(src_sent.encode('utf-8')+'\n')
                tgt_f.write(tgt_sent.encode('utf-8')+'\n')
    print "Done in", time.time()-start_time, "seconds"
    
