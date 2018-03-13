# System Combination for NMT and SMT

It is a fact that m2scorer sometimes takes extremely long time to evaluate an NMT output. NMT generates an output on the fly and does not take into consideration that GEC does not modify the translation much

# Data

- nmt.big.tok.txt = /home/ld-sgdev/tam\_hoang/Projects/Shared/GEC/mlconvgec2018/output.big\_data.txt/output.tok.txt
(the fairseq model trained on a big lang8 - custom version)

- smt.lang8v2.tok.txt = /home/ld-sgdev/tam\_hoang/Projects/Shared/GEC/smtgec2017/my-exp/evaluation/conll14.cleaned.1 
(the moses model trained on official lang8v2 - with modification)

... to be continued
