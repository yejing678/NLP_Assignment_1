# -*- coding: utf-8 -*-
import os.path
import io
import sys
import re
import json
import pickle
import pandas as pd
import urllib3
import requests
import bs4
from bs4 import BeautifulSoup
from tqdm import tqdm
from time import sleep
from pathlib import Path


sys.path.append(os.pardir)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')
urllib3.disable_warnings()
proxies = {"http": None, "https": None}
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 "
                  "Safari/537.36 "
}


def get_novel_infos_by_page(url):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = list(list(soup.find_all("table")[0].children)[1].children)
    novel_infos = []
    for tag in tqdm(result):
        if isinstance(tag, bs4.element.Tag) and "onmouseover" in tag.attrs and tag.attrs[
            "onmouseover"] == "this.bgColor = '#ffffff';":
            novel = list(list(tag.children)[3].children)[1]
            novel_href = novel.attrs["href"]
            novel_id = int(re.match(r"onebook.php\?novelid=([0-9]+)", novel_href).groups()[0])
            novel_name = novel.contents[0]
            print("Name:", novel_name, "  Id:", novel_id)
            novel_infos.append((novel_name, novel_id, get_chapter_num_by_novel_id(novel_id)))
    return novel_infos


def get_chapter_num_by_novel_id(novel_id):
    url = "https://www.jjwxc.net/onebook.php?novelid={}".format(novel_id)
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.content, 'html.parser')
    result = list(list(soup.find_all(id="oneboolt")[0].children)[1].children)
    chapter_id = -1
    for tag in result:
        if isinstance(tag, bs4.element.Tag) and "itemprop" in tag.attrs and tag.attrs["itemprop"] == "chapter":
            target_text = str(list(list(tag.children)[1].children)).strip()
            chapter_id = [int(s) for s in target_text.split() if s.isdigit()][0]
            # print(chapter_id)
    chapter_num = chapter_id
    return chapter_num


def scrape_by_novel_id_and_chapter_num(novel_id, chapter_num, output_dir, leave=False):
    all_text = []
    for c_id in tqdm(range(1, chapter_num + 1), leave=leave):
        url = "https://www.jjwxc.net/onebook.php?novelid={}&chapterid={}".format(novel_id, c_id)
        resp = requests.get(url, verify=False)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.content, 'html.parser')
        result = soup.find_all("br")
        for tag in result:
            if tag.text is not None and tag.nextSibling is not None:
                if isinstance(tag.text, str) and isinstance(tag.nextSibling, str):
                    single_text = str(tag.text + tag.nextSibling).strip()
                    if single_text:
                        all_text.append([single_text])

    result_file = "./{}/novel_{}.txt".format(output_dir, novel_id)
    print("Writing to file {}...".format(result_file))
    with open(result_file, "w", encoding='UTF-8') as f:
        for line in tqdm(all_text, leave=leave):
            f.write("{}\n".format(line[0]))

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


if __name__ == '__main__':
    # some settings
    output_dir = "new_novels"
    start_page = 1
    end_page = 10
    dic = {}

    # novel infos
    print("Preparing to get novel infos...")
    novel_infos = []
    for page_num in range(start_page, end_page + 1):
        print("Searching Page {}...".format(page_num))
        url = "https://www.jjwxc.net/bookbase_slave.php?t=0&booktype=free&opt=&page={}&endstr=&orderstr=4".format(
            page_num)
        single_page_novel_infos = get_novel_infos_by_page(url)
        novel_infos.extend(single_page_novel_infos)
    print("Saving metadata files...")
    save_json(novel_infos, os.path.join(output_dir, "metadata.json"), ensure_ascii=False)

    # use this code to read from the metadata.json
    content = load_json(os.path.join(output_dir, "metadata.json"), encoding="utf-8")

    # start scraping
    print("Start scraping {} novels...".format(len(novel_infos)))
    pbar = tqdm(novel_infos)
    for (novel_name, novel_id, chapter_num) in pbar:
        pbar.set_description("{}".format(novel_name))
        scrape_by_novel_id_and_chapter_num(novel_id, chapter_num, output_dir)
