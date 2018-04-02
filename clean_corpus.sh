#!/bin/bash

# Download preprocessing scripts from Moses
if [ ! -f replace-unicode-punctuation.perl ]; then
  wget https://github.com/moses-smt/mosesdecoder/raw/master/scripts/tokenizer/replace-unicode-punctuation.perl
fi
if [ ! -f remove-non-printing-char.perl ]; then
  wget https://github.com/moses-smt/mosesdecoder/raw/master/scripts/tokenizer/remove-non-printing-char.perl
fi
if [ ! -f normalize-punctuation.perl ]; then
  wget https://github.com/moses-smt/mosesdecoder/raw/master/scripts/tokenizer/normalize-punctuation.perl
fi
if [ ! -f clean-corpus-n.perl ]; then
  wget https://github.com/moses-smt/mosesdecoder/raw/master/scripts/training/clean-corpus-n.perl
fi

python preprocess_lang8.py lang-8-20111007-L1-v2.dat lang-8-v2 lang-8-v2.keep src tgt
for prefix in lang-8-v2 lang-8-v2.keep; do
  for suf in src tgt; do
    cat $prefix.$suf \
      | perl replace-unicode-punctuation.perl \
      | perl remove-non-printing-char.perl \
      | perl normalize-punctuation.perl \
      | python nltk_tokenize.py > $prefix.tok.$suf
  done
done
perl clean-corpus-n.perl lang-8-v2.tok src tgt lang-8-v2.clean 1 80
perl clean-corpus-n.perl lang-8-v2.keep.tok src tgt lang-8-v2.keep.clean 1 80
