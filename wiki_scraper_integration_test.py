from wiki_scraper import Scraper
import pytest

if __name__ == '__main__':
    URL = "https://bulbapedia.bulbagarden.net/wiki/Main_Page"
    WebScraper = Scraper(URL , use_local_html_file_instead=True)

