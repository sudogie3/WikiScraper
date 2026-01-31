from wiki_scraper import Scraper

def test_summary():
    webScraper = Scraper(use_local_html_file_instead=True)
    expected = ("Rocket-dan, literally Rocket Gang) is a villainous team in pursuit of evil"
                " and the exploitation of Pokémon. The organization is based in the Kanto and Johto regions,"
                " with a small outpost in the Sevii Islands.")
    summary = webScraper.summary('Team_Rocket')
    return summary == expected

if __name__ == '__main__':
    import pytest
    exit(pytest.main())


