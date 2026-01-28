import argparse
import csv
import json
import time
import wordfreq
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


# Musze wybrać jakiego typu ma być to wiki (kanye west , marvel , ekipa friza)


class Scraper:

    def __init__(self, link_URL, use_local_html_file_instead=False):
        self.link = link_URL
        self.use_lokal = use_local_html_file_instead
        self.used_count_words = False
        self.language = ""

    def SiteDownloader(self, URL):
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Nie ma takiej strony: {URL} lub nie działa")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        return soup

    def summary(self, phrase):
        if phrase is None:
            return None
        phrase_tmp = phrase.replace(" ", "_")
        URL_tmp = self.link + "/" + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        # zrobić to w div class
        div = soup.find("div", class_="mw-content-ltr mw-parser-output")
        if div == None:
            print(f"Brak artykułu an stronie {URL_tmp}")
            return None
        para = div.find("p").get_text()
        print(para)

    def table(self, phrase, number, first_row_header=False):
        if phrase is None:
            return None
        phrase_tmp = phrase.replace(" ", "_")
        URL_tmp = self.link + "/" + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)

        tables = soup.find_all("table")
        if number > len(tables):
            print(f"Na stronie {URL_tmp} nie ma tylu tabel")
            return None

        table = tables[number - 1]
        rows = table.find_all("tr")
        tableForPandas = []
        for row in rows:
            dataRow = row.find_all(["td", "th", "thead"])
            dataRowText = [data.get_text().strip() for data in dataRow]

            tableForPandas.append(pd.Series(dataRowText))
            print(dataRowText)

        df = pd.DataFrame(tableForPandas)

        if first_row_header:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)

        df = df.set_index(df.columns[0])
        print(df)
        with open(f"{phrase_tmp}.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(tableForPandas)
        return None

    def count_words(self, phrase):
        if phrase is None:
            return None
        phrase_tmp = phrase.replace(" ", "_")
        soup = self.SiteDownloader(self.link + "/" + phrase_tmp)
        if self.language == "":
            response = requests.get(self.link + "/" + phrase_tmp)
            self.language = response.headers.get("Content-Language")

        if soup is None:
            return

        text = soup.find("div", class_="mw-content-ltr mw-parser-output").get_text(
            strip=True, separator=" "
        )

        words = []
        word = ""
        for letter in text:
            if letter == " ":
                words.append(word)
                word = ""
            elif letter.isalpha() or letter == "-":
                word += letter.lower()

        # deleting hyperlinks
        i = 0
        while i < len(words):
            word = words[i]
            if word == "" or word[-1] == "-":
                words.pop(i)
            elif len(word) >= 4 and word[:4] == "http":
                words.pop(i)
            elif len(word) >= 3 and word[:3] == "www":
                words.pop(i)
            else:
                i += 1

        setOfWords = {}
        for word in words:
            if word not in setOfWords:
                setOfWords[word] = 1
            else:
                setOfWords[word] += 1
        print()
        with open("./word-count.json", "w", encoding="utf-8") as file:
            json.dump(setOfWords, file, ensure_ascii=False)
        self.used_count_words = True
        return True

    def analyze_relative_word_frequency(self, mode, count, chart=None):
        if not self.used_count_words:
            return None
        if (
            mode not in {"article", "language"}
            or count < 0
            or (
                chart != None
                and len(chart) < 4
                and chart[len(chart) - 4 : len(chart)] != ".png"
            )
        ):
            return None

        with open("./word-count.json", "r", encoding="utf-8") as file:
            siteData = json.load(file)
        setFrequencyLang = {}
        setFrequencyArticle = {}
        sumWords = 0
        mostFrequencyLang = wordfreq.word_frequency(
            wordfreq.top_n_list(n=1, lang=self.language)[0], self.language
        )

        for word in siteData:
            setFrequencyLang[word] = (
                wordfreq.word_frequency(word, lang=self.language) / mostFrequencyLang
            )
            sumWords += siteData[word]
        mostFrequencyArticle = max(siteData.values()) / sumWords

        for word in siteData:
            setFrequencyArticle[word] = (
                siteData[word] / sumWords
            ) / mostFrequencyArticle

        df1 = pd.DataFrame(
            {
                "word": setFrequencyLang.keys(),
                "frequency in wiki language": setFrequencyLang.values(),
            }
        )
        df2 = pd.DataFrame(
            {
                "word": setFrequencyArticle.keys(),
                "frequency in article": setFrequencyArticle.values(),
            }
        )
        pd.set_option(
            "display.float_format", "{:.4f}".format
        )  # wyswietlaj w zmiennoprzecinkowej , nie w naukowej

        df = pd.merge(df2, df1, on="word", how="inner")

        if mode == "article":
            df = df.sort_values("frequency in article", ascending=False)
        if mode == "language":
            df = df.sort_values("frequency in wiki language", ascending=False)

        df = df.head(count)
        print(df)

        if chart is None:
            return None

        df.set_index("word")[
            ["frequency in article", "frequency in wiki language"]
        ].plot(kind="bar", figsize=(10, 5))
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(chart)
        return None

    def help_auto_count_words(self, phrase, depth, wait, alreadyProcessed):

        with open("./word-count.json", "r", encoding="utf-8") as file:
            alreadyProcessdWords = json.load(file)

        time.sleep(wait)  # zasypiamy na wait sekund

        self.count_words(phrase)
        with open("./word-count.json", "r", encoding="utf-8") as file:
            newWords = json.load(file)

        # merguje je
        for k, v in alreadyProcessdWords.items():
            if k in newWords:
                newWords[k] += v
            else:
                newWords[k] = v

        with open("./word-count.json", "w", encoding="utf-8") as file:
            json.dump(newWords, file, ensure_ascii=False)
        if depth <= 0:
            return

        soup = self.SiteDownloader(self.link + "/" + phrase)

        para = soup.find_all("p")
        hyperlinks = []
        for paragraph in para:
            tmp_link = paragraph.find("a")
            if (
                tmp_link
                and ("href" in tmp_link.attrs)
                and (len(tmp_link["href"]) >= 6)
                and (tmp_link["href"][:6] == "/wiki/")
            ):
                hyperlinks.append(tmp_link["href"][6:])

        for hyperlink in hyperlinks:
            if hyperlink not in alreadyProcessed:
                alreadyProcessed.append(hyperlink)
                self.help_auto_count_words(hyperlink, depth - 1, wait, alreadyProcessed)

    def auto_count_words(self, phrase, depth, wait):
        if phrase is None or depth < 0 or wait < 0:
            return
        # szukamy hyperlączy
        soup = self.SiteDownloader(self.link + "/" + phrase)

        para = soup.find_all("p")
        hyperlinks = []
        for paragraph in para:
            tmp_link = paragraph.find("a")
            if (
                tmp_link
                and ("href" in tmp_link.attrs)
                and (len(tmp_link["href"]) >= 6)
                and (tmp_link["href"][:6] == "/wiki/")
            ):
                hyperlinks.append(tmp_link["href"][6:])

        self.count_words(phrase)
        alreadyProcessed = []
        for hyperlink in hyperlinks:
            if hyperlink not in alreadyProcessed:
                alreadyProcessed.append(hyperlink)
                self.help_auto_count_words(hyperlink, depth - 1, wait, alreadyProcessed)


def creating_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--summary", type=str, default=None, help="searching phrase")

    parser.add_argument(
        "--table", type=str, default=None, help="searching for a table in ..."
    )

    parser.add_argument(
        "--number", type=int, default=-1, help="searching for n-th table"
    )

    parser.add_argument(
        "--first-row-is-header",
        type=bool,
        default=False,
        help="if this argument is given then we claim that first row is a header",
    )

    parser.add_argument(
        "--count-words", type=str, default=None, help="counting in given phrase words"
    )

    parser.add_argument(
        "--analyze-relative-word-frequency",
        action="store_true",
        help="shows the difference between frequencies in the words in article",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=-1,
        help="number of elements in the table which we display",
    )

    parser.add_argument(
        "--mode",
        type=str,
        default="",
        help="sorts the relative-word-frequencies table by the given arg",
    )

    parser.add_argument(
        "--chart",
        type=str,
        default=None,
        help="creates a chart of the relative-word-frequency analiz",
    )

    parser.add_argument(
        "--auto-count-words",
        type=str,
        default=None,
        help="counting in given phrase words and going into hyperlinks",
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=-1,
        help="a number which says how deep would our recursive stack be",
    )

    parser.add_argument(
        "--wait",
        type=float,
        default=-1,
        help="a number which says how much time would we wait between calling another request",
    )

    args = parser.parse_args()

    return args


class Control:
    def __init__(self, URL):
        self.args = creating_parser()
        self.scraper = Scraper(URL)

    def iterateArguments(self):
        if self.args == {}:
            print("Nie podano żadnych argumentów")
            return

        self.scraper.summary(self.args.summary)

        self.scraper.table(
            self.args.table, self.args.number, self.args.first_row_is_header
        )

        self.scraper.count_words(self.args.count_words)
        if self.args.analyze_relative_word_frequency:
            self.scraper.analyze_relative_word_frequency(
                self.args.mode, self.args.count, self.args.chart
            )

        self.scraper.auto_count_words(
            self.args.auto_count_words, self.args.depth, self.args.wait
        )


if __name__ == "__main__":
    URL = "https://bulbapedia.bulbagarden.net/wiki"
    # controler = Control(URL)
    # controler.iterateArguments()
    obiekt = Scraper(URL)
    obiekt.table("Kanto", 8, True)
    obiekt.table("Type", 2, True)
