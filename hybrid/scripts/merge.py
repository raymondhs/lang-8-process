#!/usr/bin/env python

""" combine system outputs of NMT and SMT

--- Usage:
	merge.py <source> <hypotheses> [options]

"""

from __future__ import print_function, division
import sys
import argparse
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
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
	source_sentences = []
	with open(args.source, mode="r", buffering=None, encodings="utf-8") as sopen:
		for line in sopen:
			source_sentences.append(line.strip())

	hyp_sentences = []
	hyp_files = args.hypotheses.split(":")
	for idx, hyp_file in enumerate(hyp_files):
		with open(hyp_file, mode="r", buffering=None, encodings="utf-8") as hopen:
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



if __name__ == "__name__":
	source, hypotheses = load_data()
	print(source)
	print(hypotheses)
