# -*- coding: utf-8 -*-
import os
import sys
import pandas as pd
import requests
import bs4
import time
import urllib3
from bs4 import BeautifulSoup
from tqdm import tqdm
from argparse import ArgumentParser
from utils import write_txt
from get_wiki_url import get_wiki_urls2

sys.path.append(os.pardir)

urllib3.disable_warnings()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36"
}


def getHTMLText(url):
    try:
        r = requests.get(url)
        r.encoding = r.apparent_encoding
        return r.text
    except:
        print("Failed!")


def get_all_url(url):
    try:
        news_list = []
        r = requests.get(url, headers=headers)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        tags = soup.find_all('a')
        for tag in tags:
            news_list.append((str(tag.get('href')).strip()))
        return news_list
    except:
        print("Failed!")


def get_text(url):
    try:
        news = ''
        r = requests.get(url, headers=headers, verify=False)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.title.text.strip()
        news += title
        for x in soup.find_all('div', {'id': ['detail']}):
            for y in x.find_all('p'):
                text = y.text.strip()
                news += text
        return news
    except:
        print("Failed!")


def get_eng_novel(home_url, N, path):
    try:
        print("getting my urls...")
        url_list = []
        for num in tqdm(range(N, N + 19)):
            my_url = home_url.format(num)
            url_list.append(my_url)

        print("scraping novel text...")
        data = ''
        dic = {}
        for i_url in tqdm(url_list):
            novel = ''
            r = requests.get(i_url, headers=headers, verify=False)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
            for x in soup.find_all('div', {'class': ['text']}):
                text = x.text.strip()
                novel += text
                data += text
            dic.setdefault(i_url, novel)
        u = list(dic.keys())
        t = list(dic.values())
        result = pd.DataFrame()
        result["url"] = u
        result["text"] = t
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        print("save to " + path)
        result.to_excel(path, engine='xlsxwriter')
        print(data)
        return data
    except:
        print("get English novel failed!")


def get_baike_text(url, num):
    dic = {}
    data = ''
    print("getting baike text...")
    for idx in tqdm(range(num, num + 20000, 1)):
        if idx % 1000 == 0:
            u = list(dic.keys())
            t = list(dic.values())
            result = pd.DataFrame()
            result["url"] = u
            result["text"] = t
            baike_save_path = "./baike/excel/data_{}.xlsx".format(idx)
            dirname = os.path.dirname(baike_save_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            print("save to " + baike_save_path)
            result.to_excel(baike_save_path, engine='xlsxwriter')
            dic = {}
        my_url = url + str(idx) + '.htm'
        text = ''
        r = requests.get(my_url, headers=headers, verify=False)
        r.encoding = "UTF-8"
        soup = BeautifulSoup(r.text, 'html.parser')
        for x in soup.find_all('div', {'class': 'para'}):
            text += x.text
        data += text
        dic.setdefault(my_url, text)
        r.close()
        time.sleep(1)
    return data


def get_wiki_text(start_url, target_url):
    try:
        print("getting wiki urls....")
        url_list = get_wiki_urls2(start_url, target_url)
        print("getting wiki text...")
        data = ''
        for i_url in tqdm(url_list):
            r = requests.get(i_url, headers=headers, verify=False)
            r.encoding = 'utf-8'
            soup = BeautifulSoup(r.text, 'html.parser')
        for x in soup.find_all('div', {'id': ['mw-content-text']}):
            for y in x.find_all('p'):
                text = y.text.strip()
                data += text
        print(data)
        return data
    except:
        print("get wiki text failed!")


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("--N", type=int, default=20000, )
    parser.add_argument("--home_url", type=str, default="http://novel.tingroom.com/jingdian/5150/{}.html",
                        help='"http://baike.baidu.com/view/";'
                             '"http://novel.tingroom.com/jingdian/5150/{}.html"')
    parser.add_argument("--baike_save_path", type=str, default="./baike/text/baike.txt")
    parser.add_argument("--novel_EN_save_path", type=str, default="./novel_EN/text/novel_5150.txt")
    parser.add_argument("--wiki_save_path", type=str, default="./wiki/text/wiki.txt")
    parser.add_argument("--novel_EN_save_path2", type=str, default="./novel_EN/xlsx/novel_5150.xlsx")
    parser.add_argument("--start_url", type=str, default="https://en.wikipedia.org/wiki/Special:Random")
    parser.add_argument("--target_url", type=str, default="https://en.wikipedia.org/wiki/Philosophy")
    args = parser.parse_args()

    EN_novels = get_eng_novel(args.home_url, 130835, args.novel_EN_save_path2)
    write_txt(EN_novels, args.novel_EN_save_path)

    # data = get_wiki_text(args.start_url, args.target_url)

    # print("="*9+"scraping baike"+"="*9)
    # baike_data = get_baike_text(home_url, args.N)
    # write_txt(baike_data, args.baike_save_path)
