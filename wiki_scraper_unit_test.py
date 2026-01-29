from wiki_scraper import Scraper
import pytest


def test_does_the_paragraph_match():
    webScraper = Scraper(use_local_html_file_instead=True)
    expected = ("Rocket-dan, literally Rocket Gang) is a villainous team in pursuit of evil"
                " and the exploitation of Pokémon. The organization is based in the Kanto and Johto regions,"
                " with a small outpost in the Sevii Islands.")
    ret = webScraper.summary('Team_Rocket')
    return ret == expected

def test_what_langauge():
    webScrper = Scraper(use_local_html_file_instead=True)
    expected_lang = "en"
    ret = webScrper.what_language_offline('Team_Rocket')
    return ret == expected_lang

def test_is_it_wiki_page():
    pass
def test_does_the_first_table_match():
    pass