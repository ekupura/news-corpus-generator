import crawler


def main():
    c = crawler.Crawler("./configuration.yml")
    c.get_news_and_export()


if __name__ == '__main__':
    main()
