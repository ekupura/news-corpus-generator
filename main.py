import crawler

urls_and_categories = [('http://news.livedoor.com/topics/category/dom/', "domestic"),
                      ('http://news.livedoor.com/topics/category/world/',  "world"),
                      ('http://news.livedoor.com/topics/category/eco/',  "economy"),
                      ('http://news.livedoor.com/topics/category/ent/',  "entertainment"),
                      ('http://news.livedoor.com/topics/category/sports/',  "sports"),
                      ('http://news.livedoor.com/article/category/52/',  "movie"),
                      ('http://news.livedoor.com/topics/category/gourmet/',  "gourmet")],


def main():
    for uc in urls_and_categories:
        summaries, articles, urls = crawler.get_news(uc[0], n_iter=1)


if __name__ == '__main__':
    main()

