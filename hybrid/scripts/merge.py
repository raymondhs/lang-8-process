#!/usr/bin/env python

""" combine system outputs of NMT and SMT

--- Usage:
	merge.py <source> <hypotheses> [options]

"""

from __future__ import print_function, division
import sys
import argparse
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument("source", type=str, help="source file containing english written by ESL")
parser.add_argument("hypotheses", type=str, help="output of system separated by colons")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")

args = parser.parse_args()

if args.verbose:
    logger.info("verbosity turned on")
    logger.warn("A lot of messages will be printed!")


def load_data():
	""" load source file and hypotheses files into memory
	return: array of sources sentences, array of hypotheses tuples
	"""
	# logger.info("read file {0}".format(args.source))
	source_sentences = []
	with open(args.source, mode="r") as sopen:
		for line in sopen:
			source_sentences.append(line.strip())

	hyp_sentences = []
	hyp_files = args.hypotheses.split(":")
	for idx, hyp_file in enumerate(hyp_files):
		with open(hyp_file, mode="r") as hopen:
			counter = 0
			for line in hopen:
				line = line.strip()
				if idx == 0:
					hyp_sentences.append([line])
				else:
					hyp_sentences[counter].append(line)
				counter += 1

	# check the length of sources and hypotheses
	assert len(source_sentences) == len(hyp_sentences), "Incorrect number of sources ({0}) and hypotheses({1})".format(len(source_sentences), len(hyp_sentences))

	return source_sentences, hyp_sentences


def score_pair(src_tok, hyp_tok):
	""" judge the potential of a hypothesis given the source token
	"""
	# if src_tok == hyp_tok:
	# 	return 0
	# count how many edit we have to make to convert src_tok into hyp_tok
	src_toks, hyp_toks = src_tok.split(), hyp_tok.split()
	src_len, hyp_len = len(src_toks), len(hyp_toks)
	
	# create a table to calculate the dp matrix
	dp = [[None for _ in range(hyp_len+1)] for _ in range(src_len+1)]

	for idx in range(hyp_len+1):
		dp[0][idx] = idx

	for idx in range(src_len+1):
		dp[idx][0] = idx

	for id1 in range(1, src_len+1):
		for id2 in range(1, hyp_len+1):
			if src_toks[id1-1] == hyp_toks[id2-1]:
				dp[id1][id2] = dp[id1-1][id2-1]
			else:
				dp[id1][id2] = min(dp[id1-1][id2-1], dp[id1][id2-1], dp[id1-1][id2]) + 1

	# score the pair by the number of edit between the two sentence
	# assume that most of the GEC sentence has at most n/4 edits with n is the length of the sources
	# each hypothesis is assigned a weight
	final_score = 0
	if dp[src_len][hyp_len] <= src_len/2 and abs(src_len - hyp_len) < 10:
		final_score = 1
	return final_score


def merge_list(source_list, hyp_list):
	""" main function to select the best hypotheses
	return: a list of the best hypotheses
	"""
	results = []
	for source, hypotheses in zip(source_list, hyp_list):
		best_hyp, best_score = source, -1  # at the beginning, the source sentence get zero score
		for hypo in hypotheses:
			score = score_pair(source, hypo)
			if score == 0:
				logger.warn("S:\t{0}".format(source))
				logger.warn("H:\t{0}\t{1}\n".format(hypo, score))
			if score > best_score:
				best_hyp, best_score = hypo, score
		results.append(best_hyp)

	return results

if __name__ == "__main__":
	source, hypotheses = load_data()
	results = merge_list(source, hypotheses)
	print("\n".join(results))
