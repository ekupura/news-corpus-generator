import requests
import re
from pprint import pprint
from bs4 import BeautifulSoup
from tqdm import tqdm

def get_article(article_url):
    # get summary
    r = requests.get(article_url)
    row_article = r.text
    soup = BeautifulSoup(row_article, features="html5lib")
    row_summary = soup.find("div", class_="summaryBody")
    if row_summary:
        summary = re.sub(" ", "", row_summary.text).strip()
    else:
        summary = None

    # get html
    r = requests.get(article_url.replace('topics', 'article'))
    row_article = r.text
    soup = BeautifulSoup(row_article, features="html5lib")
    row_article = soup.find("span", itemprop="articleBody")
    if row_article:
        article = row_article.text.replace("\u3000", " ").strip()
    else:
        article = None

    return summary, article


def get_article_list(root_url):
    r = requests.get(root_url)
    row_article = r.text
    soup = BeautifulSoup(row_article, features="html5lib")
    soup_article_list = soup.find("ul", class_="articleList").find_all("a")
    article_list = [li.get("href") for li in soup_article_list]
    return article_list


def get_news(category_root_url, n_iter):
    summaries, articles, urls = [], [], []
    for i in tqdm(range(n_iter)):
        iter_url = category_root_url + '?p=' + str(n_iter + 1)
        article_url_list = get_article_list(iter_url)
        for article_url in article_url_list:
            s, a = get_article(article_url)
            summaries.append(s)
            articles.append(a)
            urls.append(article_url)
    return summaries, articles, urls

