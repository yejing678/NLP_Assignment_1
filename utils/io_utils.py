# -*- coding: utf-8 -*-
# file: vocab_utils.py
# github: https://github.com/CogNLP/CogKTR/blob/main/cogktr/utils/io_utils.py
import os, sys
import re
from pathlib import Path
import json
import torch.nn as nn
import torch
import pickle
import pandas as pd
from tqdm import tqdm
import jieba

sys.path.append(os.pardir)


def save_json(data, file_path):
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'w') as f:
        json.dump(data, f, indent=4)


def load_json(file_path):
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'r') as f:
        data = json.load(f)
    return data


def save_pickle(data, file_path):
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'wb') as f:
        pickle.dump(data, f)


def load_pickle(file_path):
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'rb') as f:
        data = pickle.load(f)
    return data


def load_model(model, model_path):
    if isinstance(model_path, Path):
        model_path = str(model_path)
    print(f"loading model from {str(model_path)} .")
    states = torch.load(model_path)
    if isinstance(model, nn.parallel.DistributedDataParallel):
        model.module.load_state_dict(states)
    else:
        model.load_state_dict(states, strict=False)
    return model


def save_model(model, model_path):
    if isinstance(model_path, Path):
        model_path = str(model_path)
    if isinstance(model, nn.DataParallel):
        model = model.module
    state_dict = model.state_dict()
    for key in state_dict:
        state_dict[key] = state_dict[key].cpu()
    torch.save(state_dict, model_path)


def write_txt(data, path):
    print("writing txt to " + path)
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    with open(path, 'w', encoding='UTF-8') as f:
        if data is not None:
            f.write(data)
            f.close()
        else:
            print('data is empty!')


def read_txt_files(dir_path):
    print("reading txt files...")
    files = os.listdir(dir_path)
    text = ''
    for file in tqdm(files):
        position = dir_path + '/' + file
        with open(position, "r", encoding='utf-8') as f:
            data = f.read()
            # Only Chinese characters are retained and all other characters are filtered
            # TODO maybe there are other data cleaning method
            data = re.sub('[^\u4e00-\u9fa5]+', '', data)
            text = text + data
    return text
