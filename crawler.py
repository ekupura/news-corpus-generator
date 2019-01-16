import requests
import requests.exceptions
import yaml
import sqlite3
from bs4 import BeautifulSoup
from tqdm import tqdm


class Crawler:
    def __init__(self, configuration_path):
        with open(configuration_path) as f:
            configuration = yaml.load(f)
        self.db_name = configuration['db_name']
        self.table_name = configuration['table_name']
        self.n_iter = configuration['n_iter']
        self.urls_and_categories = list(configuration['urls'].items())

    def get_article(self, article_url):
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

    def get_article_list(self, root_url):
        r = requests.get(root_url)
        row_article = r.text
        soup = BeautifulSoup(row_article, features="html5lib")
        soup_article_list = soup.find("ul", class_="articleList").find_all("a")
        article_list = [li.get("href") for li in soup_article_list]
        return article_list

    def get_news_and_export(self):
        for uc in self.urls_and_categories:
            category_root_url, category = uc[1], uc[0]
            for i in range(self.n_iter):
                print(category + ":" + str(i + 1) + "/" + str(self.n_iter))
                iter_url = category_root_url + '?p=' + str(i + 1)
                article_url_list = self.get_article_list(iter_url)
                summaries, articles, urls = [], [], []
                for article_url in article_url_list:
                    try:
                        s, a = self.get_article(article_url)
                    except requests.exceptions.ConnectionError:
                        import traceback
                        traceback.print_exc()
                        continue
                    summaries.append(s)
                    articles.append(a)
                    urls.append(article_url)
                self.insert_into_database(summaries, articles, urls, category)
        return None

    def insert_into_database(self, summaries, articles, urls, category):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        create_table_sql = "CREATE TABLE IF NOT EXISTS " + self.table_name + \
                           " (summary TEXT, article TEXT, urls TEXT, category TEXT)"
        insert_sql = "INSERT INTO " + self.table_name + " VALUES (?, ?, ?, ?)"
        values = [(s, a, u, category) for s, a, u in zip(summaries, articles, urls)]
        cursor.execute(create_table_sql)
        cursor.executemany(insert_sql, values)
        connection.commit()
        connection.close()


