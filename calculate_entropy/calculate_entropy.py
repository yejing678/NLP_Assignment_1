# -*- coding: utf-8 -*-
import os
import sys
import re
import numpy as np
import jieba
from scipy.stats import entropy
from math import *
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser
from utils import Vocabulary
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def entropy1(labels, base=None):
    value, counts = np.unique(labels, return_counts=True)
    return entropy(counts, base=base)


def entropy2(labels, base=None):
    """ Computes entropy of label distribution. """

    n_labels = len(labels)

    if n_labels <= 1:
        return 0

    value, counts = np.unique(labels, return_counts=True)
    probs = counts / n_labels
    n_classes = np.count_nonzero(probs)

    if n_classes <= 1:
        return 0

    ent = 0.

    # Compute entropy
    base = e if base is None else base
    for i in probs:
        ent -= i * log(i, base)

    return ent


def entropy3(labels, base=None):
    vc = pd.Series(labels).value_counts(normalize=True, sort=False)
    base = e if base is None else base
    return -(vc * np.log(vc) / np.log(base)).sum()


def entropy4(labels, base=None):
    value, counts = np.unique(labels, return_counts=True)
    norm_counts = counts / counts.sum()
    base = e if base is None else base
    return -(norm_counts * np.log(norm_counts) / np.log(base)).sum()


def read_csv_data(data_path, entropy_type):
    all_words = []
    print("reading csv data...")
    df = pd.read_excel(data_path, index_col=0)
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        text_piece = row["text"]
        if (isinstance(text_piece, str)):
            text_piece = re.sub('[^\u4e00-\u9fa5]+', '', text_piece)
            if entropy_type == "tokens":
                seg_generator = jieba.cut("".join(text_piece), use_paddle=True)
                seg_list = list(seg_generator)
            else:
                seg_list = list(text_piece)
            all_words.extend(seg_list)
    return all_words


def read_novel_text(novel_path, entropy_type, language):
    all_words = []
    print("reading text data...")
    novel_files = os.listdir(novel_path)
    for novel_file in tqdm(novel_files):
        with open(os.path.join(novel_path, novel_file), "r", encoding='UTF-8') as f:
            lines = f.readlines()
            processed_lines = [line.rstrip() for line in lines]
            for line in processed_lines:
                # TODO improve data cleaning method
                if language == "zh":
                    line = re.sub('[^\u4e00-\u9fa5]+', '', line)
                    if entropy_type == "tokens":
                        seg_generator = jieba.cut("".join(line), use_paddle=True)
                        seg_list = list(seg_generator)
                    else:
                        seg_list = list(line)
                elif language == "en":
                    line = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", line)
                    seg_list = list(line)

                all_words.extend(seg_list)
    return all_words


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--dir_path", type=str,
                        default="/home/jye/ABSA/homework/nlp/NLP homework/NLP homework/new_novels/",
                        help='novel_path = "./new_novels";'
                             'baike_file = r"baike/data-baike.xlsx"')
    parser.add_argument("--entropy_type", type=str, default="characters", help="select characters or tokens")
    parser.add_argument("--language", type=str, default="zh", help="zh or en")
    parser.add_argument("--domain", type=str, default="novel", help="novel_zh, novel_en, wiki, baike")
    args = parser.parse_args()

    all_words = read_novel_text(args.dir_path, args.entropy_type, args.language)
    logger.info("{} {} is detected.".format(len(all_words), args.entropy_type))

    print("Creating vocab...")
    vocab = Vocabulary()
    vocab.add_sequence(all_words)
    vocab.create()

    print("Calculating entropy...")
    all_word_ids = list(map(vocab.label2id_dict.get, all_words))
    entropy_result = entropy2(all_word_ids)
    logger.info("the entropy of {}".format(entropy_result))

    log_file = '{}-{}-{}'.format(args.language, args.entropy_type, args.domain)
    logger.addHandler(logging.FileHandler(log_file))
