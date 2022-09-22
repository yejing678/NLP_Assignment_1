# -*- coding: utf-8 -*-
# file: vocab_utils.py
# github: https://github.com/CogNLP/CogKTR/blob/main/cogktr/utils/vocab_utils.py

class Vocabulary():
    def __init__(self):
        self.label_set = set()
        self.defined_label2id_dict = dict()
        self.label2id_dict = {}
        self.id2label_dict = {}

    def __len__(self):
        return len(self.label_set)

    def add(self, label):
        self.label_set.add(label)

    def add_sequence(self, labels):
        for label in labels:
            self.add(label)

    def add_dict(self, defined_label2id_dict):
        # TODO:Resolve dictionary key value pair conflicts situation
        # TODO:Resolve different names have same id
        for label, id in defined_label2id_dict.items():
            if label not in self.defined_label2id_dict:
                self.defined_label2id_dict[label] = id
                self.label_set.add(label)

    def create(self):
        label_list = list(self.label_set)
        label_list.sort()
        defined_label_set = set()
        for label, id in self.defined_label2id_dict.items():
            self.label2id_dict[label] = id
            self.id2label_dict[id] = label
            defined_label_set.add(label)
            if id >= len(label_list) or id < 0:
                raise IndexError("Defined dict id must smaller than label num and bigger than 0.")
        inserting_label_set = self.label_set - defined_label_set
        inserting_label_list = list(inserting_label_set)
        inserting_label_list.sort()
        inserting_index = 0
        for id in range(len(self.label_set)):
            if id not in self.id2label_dict.keys():
                self.label2id_dict[inserting_label_list[inserting_index]] = id
                self.id2label_dict[id] = inserting_label_list[inserting_index]
                inserting_index += 1
        self.label2id_dict = dict(sorted(self.label2id_dict.items(), key=lambda x: x[1]))
        self.id2label_dict = dict(sorted(self.id2label_dict.items(), key=lambda x: x[0]))

    def label2id(self, word):
        return self.label2id_dict[word]

    def id2label(self, id):
        return self.id2label_dict[id]

    def labels2ids(self, words):
        return [self.label2id(word) for word in words]

    def ids2labels(self, ids):
        return [self.id2label(id) for id in ids]

    def get_label2id_dict(self):
        return self.label2id_dict

    def get_id2label_dict(self):
        return self.id2label_dict