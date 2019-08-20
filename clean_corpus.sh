#!/bin/bash

echo 'Cloning Moses github repository (for tokenization scripts)...'
git clone https://github.com/moses-smt/mosesdecoder.git

SCRIPTS=mosesdecoder/scripts

python preprocess_lang8.py \
  -d lang-8-20111007-L1-v2.dat \
  -o lang-8-v2.out \
  -k lang-8-v2.keep \
  -j 4

for pref in lang-8-v2.out lang-8-v2.keep; do
  cut -f1 $pref > $pref.src
  cut -f2 $pref > $pref.tgt
  for suf in src tgt; do
    cat $pref.$suf \
      | perl $SCRIPTS/tokenizer/replace-unicode-punctuation.perl \
      | perl $SCRIPTS/tokenizer/remove-non-printing-char.perl \
      | perl $SCRIPTS/tokenizer/normalize-punctuation.perl \
      | python nltk_tokenize.py > $pref.tok.$suf
  done
done
perl $SCRIPTS/training/clean-corpus-n.perl lang-8-v2.out.tok src tgt lang-8-v2.out.clean 1 80
perl $SCRIPTS/training/clean-corpus-n.perl lang-8-v2.keep.tok src tgt lang-8-v2.keep.clean 1 80
