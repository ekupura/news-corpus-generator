import requests
import re
import sqlite3
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
        summary = row_summary.text.replace(" ", "").strip().replace("\n", "\t")
    else:
        summary = ""

    # get html
    r = requests.get(article_url.replace('topics', 'article'))
    row_article = r.text
    soup = BeautifulSoup(row_article, features="html5lib")
    row_article = soup.find("span", itemprop="articleBody")
    if row_article:
        copy_soup = row_article
        if copy_soup.find("script"):
            row_article.find("script").decompose()
        article = row_article.text.replace("\u3000", " ").strip()
    else:
        article = ""

    return summary, article


def get_article_list(root_url):
    r = requests.get(root_url)
    row_article = r.text
    soup = BeautifulSoup(row_article, features="html5lib")
    soup_article_list = soup.find("ul", class_="articleList").find_all("a")
    article_list = [li.get("href") for li in soup_article_list]
    return article_list


def get_news_and_export(category_root_url, category, n_iter):
    for i in tqdm(range(n_iter)):
        iter_url = category_root_url + '?p=' + str(i + 1)
        article_url_list = get_article_list(iter_url)
        summaries, articles, urls = [], [], []
        for article_url in article_url_list:
            s, a = get_article(article_url)
            summaries.append(s)
            articles.append(a)
            urls.append(article_url)
        insert_into_database(summaries, articles, urls, category)
    return None


def insert_into_database(summaries, articles, urls, category):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    create_table_sql = "CREATE TABLE IF NOT EXISTS " + table_name + \
                       " (summary TEXT, article TEXT, urls TEXT, category TEXT)"
    insert_sql = "INSERT INTO " + table_name + " VALUES (?, ?, ?, ?)"
    values = [(s, a, u, category) for s, a, u in zip(summaries, articles, urls)]
    cursor.execute(create_table_sql)
    cursor.executemany(insert_sql, values)
    connection.commit()
    connection.close()


urls_and_categories = [('http://news.livedoor.com/topics/category/dom/', "domestic"),
                       ('http://news.livedoor.com/topics/category/world/',  "world"),
                       ('http://news.livedoor.com/topics/category/eco/',  "economy"),
                       ('http://news.livedoor.com/topics/category/ent/',  "entertainment"),
                       ('http://news.livedoor.com/topics/category/sports/',  "sports"),
                       ('http://news.livedoor.com/article/category/52/',  "movie"),
                       ('http://news.livedoor.com/topics/category/gourmet/',  "gourmet")]

db_name = "./news.db"
table_name = "news"
for uc in urls_and_categories:
    get_news_and_export(uc[0], uc[1], 1)


