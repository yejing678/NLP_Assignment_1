# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import bs4
import requests
from tqdm import tqdm
import re
from pathlib import Path
import pickle
import os
import json


def scrape_by_novel_name_and_chapter_num_english(novel_name, chapter_num, output_dir, leave=False):
    all_text = []
    for c_id in tqdm(range(1, chapter_num + 1), leave=leave):
        url = "https://allnovel.net/{}/page-{}.html".format(novel_name, c_id)
        resp = requests.get(url)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.content, 'html.parser')
        for x in soup.find_all('div', {"class": ['des_novel']}):
            for y in x.find_all('p'):
                text = y.text.strip()
                all_text.append(text)

    result_file = "./{}/novel_{}.txt".format(output_dir, novel_name)
    # print("Writing to file {}...".format(result_file))
    with open(result_file, "w") as f:
        for line in tqdm(all_text, leave=leave):
            f.write("{}\n".format(line))


def get_chapter_num_by_novel_name(novel_name):
    url = "https://allnovel.net/{}.html".format(novel_name)
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = soup.find_all('table', {"class": ['table table-bordered table-striped']})[0]
    chapter_num = len(result.find_all("a"))
    return chapter_num


def get_novel_infos_by_page_english(url):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.content, 'html.parser')
    table = soup.find_all('div', {"class": ['col-sm-12 list-novel']})[0]

    novel_infos = []
    for novel_href_info in tqdm(table.find_all("a")):
        novel_href = novel_href_info.attrs["href"]
        novel_name = re.match(r"\/([^.]+).html", novel_href).groups()[0]
        novel_infos.append((novel_name, get_chapter_num_by_novel_name(novel_name)))
    return novel_infos


def load_json(file_path, **kwargs):
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'r') as f:
        data = json.load(f, **kwargs)
    return data


def save_json(data, file_path, **kwargs):
    dirname = os.path.dirname(file_path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    if not isinstance(file_path, Path):
        file_path = Path(file_path)
    with open(str(file_path), 'w') as f:
        json.dump(data, f, indent=4, **kwargs)


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


if __name__ == '__main__':
    # some settings
    output_dir = "novels_en"
    start_page = 1
    end_page = 2

    # novel infos
    print("Preparing to get novel infos...")
    novel_infos = []
    for page_num in range(start_page, end_page + 1):
        print("Searching Page {}...".format(page_num))
        url = "https://allnovel.net/romance.html?page={}".format(page_num)
        single_page_novel_infos = get_novel_infos_by_page_english(url)
        novel_infos.extend(single_page_novel_infos)

    print("Saving metadata files...")
    save_json(novel_infos, os.path.join(output_dir, "metadata.json"), ensure_ascii=False)

    # use this code to read from the metadata.json
    # content = load_json(os.path.join(output_dir, "metadata.json"), encoding="utf-8")

    # start scraping
    print("Start scraping {} novels...".format(len(novel_infos)))
    pbar = tqdm(novel_infos)
    for (novel_name, chapter_num) in pbar:
        pbar.set_description("{}".format(novel_name))
        scrape_by_novel_name_and_chapter_num_english(novel_name, chapter_num, output_dir)
