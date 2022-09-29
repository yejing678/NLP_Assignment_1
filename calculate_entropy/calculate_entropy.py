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
from time import strftime, localtime
from nltk import word_tokenize
from nltk.corpus import stopwords
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))
delete_words = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
stops = set(stopwords.words("english"))


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


def read_text(novel_path, entropy_type, language, percentage):
    all_words = []
    print("reading text data...")
    novel_files = os.listdir(novel_path)
    novels_num = len(novel_files)
    num = int(novels_num * percentage)
    for novel_file in tqdm(novel_files[:num]):
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
                    if entropy_type == "tokens":
                        seg_list = word_tokenize(line)
                        seg_list = [word for word in seg_list if word not in delete_words]
                        # seg_list = re.findall(r'[A-Za-z0-9_]+', line)
                        # seg_list = line.strip('').split(' ')
                        # print(seg_list)
                    else:
                        line = re.sub(u"([^\u0041-\u005a\u0061-\u007a])", "", line)
                        seg_list = list(line)

                all_words.extend(seg_list)
    return all_words


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--dir_path", type=str,
                        default="/home/jye/Homework/web_crawler/novels_en/",
                        help='novel_zh_path = "./web_crawler/novels_zh/";'
                             'novel_en_path = "./web_crawler/novels_en/";'
                             'baike_file = ./web_crawler/baike/txt/')
    parser.add_argument("--entropy_type", type=str, default="tokens", help="select characters or tokens")
    parser.add_argument("--language", type=str, default="en", help="zh or en")
    parser.add_argument("--domain", type=str, default="novel_en", help="novel_zh, novel_en, wiki, baike")
    args = parser.parse_args()

    percentages = [0.1, 0.2, 0.5, 0.8, 1]
    for percentage in percentages:
        all_words = read_text(args.dir_path, args.entropy_type, args.language, percentage=0.5)
        logger.info("{}% of data is loaded.".format(percentage))
        logger.info("{} {} are detected.".format(len(all_words), args.entropy_type))

        print("Creating vocab...")
        vocab = Vocabulary()
        vocab.add_sequence(all_words)
        vocab.create()

        print("Calculating entropy...")
        all_word_ids = list(map(vocab.label2id_dict.get, all_words))
        entropy_result = entropy2(all_word_ids)
        logger.info("the entropy is {}".format(entropy_result))

    log_file = '{}-{}-{}-{}'.format(args.language, args.entropy_type, args.domain,
                                    strftime("%y%m%d-%H%M", localtime()))
    logger.addHandler(logging.FileHandler(log_file))

