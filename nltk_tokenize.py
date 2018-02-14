#!/usr/bin/env python

import sys
from nltk import word_tokenize

for line in sys.stdin:
    line = line.decode('utf-8').strip()
    print ' '.join(word_tokenize(line)).encode('utf-8')
