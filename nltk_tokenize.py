#!/usr/bin/env python

import sys
from nltk import word_tokenize

for line in sys.stdin:
    print(' '.join(word_tokenize(line)).strip())
