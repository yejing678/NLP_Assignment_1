import time
import urllib
import bs4
import requests


def find_first_link(url):
    response = requests.get(url)
    html = response.text
    soup = bs4.BeautifulSoup(html, "html.parser")
    content_div = soup.find(id="mw-content-text").find(class_="mw-parser-output")
    article_link = None
    for element in content_div.find_all("p", recursive=False):
        if element.find("a", recursive=False):
            article_link = element.find("a", recursive=False).get('href')
            break
    if not article_link:
        return
    first_link = urllib.parse.urljoin('https://en.wikipedia.org/', article_link)
    return first_link


def continue_crawl(search_history, target_url, max_steps=100):
    if search_history[-1] == target_url:
        print("We've found the target article!")
        return False
    elif len(search_history) > max_steps:
        print("The search has gone on suspiciously long, aborting search!")
        return False
    elif search_history[-1] in search_history[:-1]:
        print("We've arrived at an article we've already seen, aborting search!")
        return False
    else:
        return True


def get_wiki_urls(article_chain, target_url):
    while continue_crawl(article_chain, target_url):
        print(article_chain[-1])
        first_link = find_first_link(article_chain[-1])
        if not first_link:
            print("We've arrived at an article with no links, aborting search!")
            break
        article_chain.append(first_link)
        time.sleep(2)


def get_wiki_urls2(start_url, target_url):
    article_chain = [start_url]
    get_wiki_urls(article_chain, target_url)

    return article_chain

# start_url = "https://en.wikipedia.org/wiki/Special:Random"
# target_url = "https://en.wikipedia.org/wiki/Philosophy"
#
# article_chain = [start_url]
# while continue_crawl(article_chain, target_url):
#     print(article_chain[-1])
#     first_link = find_first_link(article_chain[-1])
#     if not first_link:
#         print("We've arrived at an article with no links, aborting search!")
#         break
#     article_chain.append(first_link)
#     time.sleep(3)

# if __name__ == '__main__':
#     start_url = "https://en.wikipedia.org/wiki/Special:Random"
#     target_url = "https://en.wikipedia.org/wiki/Philosophy"
#     print(get_wiki_urls2(start_url,target_url))



