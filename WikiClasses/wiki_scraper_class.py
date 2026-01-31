import csv
import json
import os.path
import time
import wordfreq
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

BannedLinks = (
    "/wiki/File:",
    "/wiki/Template:",
    "/wiki/MediaWiki:",
    "/wiki/User:",
    "/wiki/Category:",
    "/wiki/Special:",
    "/wiki/Help:",
)


def whatLanguageOffline(phrase):
    """Function that takes the HTML code and gets the language"""
    phrase_tmp = phrase.replace(" ", "_")
    path = f"WikiPages/{phrase_tmp}.html"
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as file:
        htmlText = file.read()
    soup = BeautifulSoup(htmlText, "html.parser")
    return soup.find("html").get("lang")



def isItWikiPage(phrase):
    """Function that checks if the sufix of the page is Wiki"""
    if phrase is None:
        return False
    prefix = "/wiki/"
    if len(phrase) >= len(prefix) and phrase[: len(prefix)] == prefix:
        return True
    return False



def extractPhrase(phrase):
    """Function that extract a phrase from link"""
    prefix = "/wiki/"
    if isItWikiPage(phrase):
        return phrase[len(prefix) :]
    return None



def siteDownloader(URL):
    """Function which downloads a site"""
    response = requests.get(URL)
    if response.status_code != 200:
        print(f"Site doesn't exist: {URL} or do not work, request code {response}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

def siteDownloaderOffline(phrase):
    """Function for taking the soup from HTML code"""
    path = f"WikiPages/{phrase}.html"
    if not os.path.exists(path):
        return False

    with open(path, "r", encoding="utf-8") as file:
        htmlText = file.read()
    soup = BeautifulSoup(htmlText, "html.parser")
    return soup

def getWordsFromText(text):
    """Function that gives table of lower case separated words"""
    #usage for count-words func
    if text is None:
        return None
    text = str(text)
    words = []
    word = ""
    for i in range(0, len(text)):
        letter = text[i]
        if letter == " ":
            words.append(word)
            word = ""
        elif letter.isalpha() or letter == "-":
            word += letter.lower()
            if i == len(text) - 1:
                words.append(word)
    return words


def InBanned(phrase):
    """Checking if the link is not article"""
    for link in BannedLinks:
        if len(phrase) >= len(link) and phrase[:len(link)] == link:
            return True
    return False



class Scraper:
    """Whole scraper class that has methods which do all the main functionalities"""
    def __init__(self, link=None, use_local_html_file_instead=False):
        if (link is not None and use_local_html_file_instead) or (link is None and not use_local_html_file_instead):
            raise ValueError(
                "Error, you can not give link and set the local_usage argument simultaneously, please choose only one"
            )
        self.link = link
        self.use_local = use_local_html_file_instead
        # used for the analyze_relative_word function
        self.used_count_words = False
        self.language = None
        # used for the auto-count function
        self.alreadyProcessed = set()
        self.first = True

    def summary(self, phrase):
        # checks if the arg is correct
        if phrase is None:
            return False
        phrase_tmp = phrase.replace(" ", "_")
        # checks if we use local file if not then we download
        if self.use_local:
            siteDownloaderOffline(phrase_tmp)
        else:
            # goes to SiteDownloader func to get the soup-ed HTML page
            URL_tmp = self.link + "/" + phrase_tmp
            soup = siteDownloader(URL_tmp)

        if soup is None:
            return False
        # get the first div
        div = soup.find("div", class_="mw-parser-output")
        if div is None:
            print(f"No article {phrase} on site {self.link}")
            return False
        para = div.find("p").get_text()
        print(para)
        return para

    def table(self, phrase, number, first_row_header=False):
        # check if the args are correct
        if phrase is None or number < 0:
            return False
        phrase_tmp = phrase.replace(" ", "_")
        URL_tmp = self.link + "/" + phrase_tmp
        if self.use_local:
            # looks for the file in the WikiPages
            soup = siteDownloaderOffline(phrase_tmp)
        else:
            soup = siteDownloader(URL_tmp)
        # finding all the tables in soup
        tables = soup.find_all("table")
        if number > len(tables):
            print(f"Site {URL_tmp} doesn't have this many tables")
            return False

        table = tables[number - 1]
        # finds all table rows
        rows = table.find_all("tr")
        tableForPandas = []
        for row in rows:
            # finda all table data, headers
            dataRow = row.find_all(["td", "th", "thead"])
            dataRowText = [data.get_text().strip() for data in dataRow]
            tableForPandas.append(pd.Series(dataRowText))

        df = pd.DataFrame(tableForPandas)
        # if the fist_row_header is marked as true, then we set it
        if first_row_header:
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        # set the first column as index
        df = df.set_index(df.columns[0])
        print(df)
        # count words that occur in table (except index and headers)
        dictOfWords = {}
        for i in range(first_row_header, len(tableForPandas)):
            for j in range(1, len(tableForPandas[i])):
                data = tableForPandas[i][j]
                if data in dictOfWords:
                    dictOfWords[data] += 1
                else:
                    dictOfWords[data] = 1

        df2 = pd.DataFrame(dictOfWords.items(), columns=["word", "count"])
        print(df2)
        # write it to csv file
        with open(f"{phrase_tmp}.csv", "w", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerows(tableForPandas)
        return df, df2

    def count_words(self, phrase):
        # checks if the arg is correct
        if phrase is None:
            return False
        phrase_tmp = phrase.replace(" ", "_")
        if self.use_local:
            soup = siteDownloaderOffline(phrase_tmp)
        else:
            URL_tmp = self.link + "/" + phrase_tmp
            soup = siteDownloader(URL_tmp)

        if soup is None:
            return False
        # set the language for analyze func
        self.language = soup.find("html").get("lang")
        # we take all text from the site (except the site's elements)
        text = soup.find("div", class_="mw-parser-output").get_text(
            strip=True, separator=" "
        )
        # we split all text and lowercase it
        words = getWordsFromText(text)

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
        # now we count words
        dictOfWords = {}
        for word in words:
            if word not in dictOfWords:
                dictOfWords[word] = 1
            else:
                dictOfWords[word] += 1
        # we put the results into json file
        with open("./word-count.json", "w", encoding="utf-8") as file:
            json.dump(dictOfWords, file, ensure_ascii=False)
        self.used_count_words = True
        return True

    def analyze_relative_word_frequency(self, mode, count, chart=None):
        # we check if we did the auto count previously mandatory
        if not self.used_count_words:
            return False
        if (
            mode not in {"article", "language"}
            or count <= 0
            or (
                chart is not None
                and len(chart) < 4
                and chart[len(chart) - 4 : len(chart)] != ".png"
            )
        ):
            return False
        # takes what inside the word-count.json file
        with open("./word-count.json", "r", encoding="utf-8") as file:
            siteData = json.load(file)
        dictFrequencyLang = {}
        dictFrequencyArticle = {}
        sumWordsInArticle = 0
        # we take the most used word for normalizing words
        mostFrequencyLang = wordfreq.word_frequency(
            wordfreq.top_n_list(n=1, lang=self.language)[0], self.language
        )
        if len(siteData) == 0:
            return False
        # normalizing the language words
        for word in siteData:
            dictFrequencyLang[word] = (
                wordfreq.word_frequency(word, lang=self.language) / mostFrequencyLang
            )
            # we count how many words are in the article
            sumWordsInArticle += siteData[word]
        mostFrequencyArticle = max(siteData.values()) / sumWordsInArticle


        for word in siteData:
            dictFrequencyArticle[word] = (
                siteData[word] / sumWordsInArticle
            ) / mostFrequencyArticle
        # we make two tables of the words and frequency
        df1 = pd.DataFrame(
            {
                "word": dictFrequencyLang.keys(),
                "frequency in wiki language": dictFrequencyLang.values(),
            }
        )
        df2 = pd.DataFrame(
            {
                "word": dictFrequencyArticle.keys(),
                "frequency in article": dictFrequencyArticle.values(),
            }
        )

        # display in floating, not in scientific
        pd.set_option("display.float_format", "{:.4f}".format)
        # we join/merge tables
        df = pd.merge(df2, df1, on="word", how="inner")

        if mode == "article":
            df = df.sort_values("frequency in article", ascending=False)
        if mode == "language":
            df = df.sort_values("frequency in wiki language", ascending=False)
        # display top count words
        df = df.head(count)
        print(df)

        if chart is None:
            return True
        # we make a plot of the table
        df.set_index("word")[
            ["frequency in article", "frequency in wiki language"]
        ].plot(kind="bar", figsize=(10, 5))
        plt.title("Frequency of some words on Wiki")
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.savefig(chart)
        return True

    def auto_count_words(self, phrase, depth, wait):
        if phrase is None or depth < 0 or wait < 0:
            return False
        # print(f"I'm in {phrase}")
        # we sleep for wait seconds
        if self.first:
            # if first all we do is single count_word
            self.count_words(phrase)
            self.first = False
        else:
            time.sleep(wait)
            # if it is not first then we take the dict from json
            with open("./word-count.json", "r", encoding="utf-8") as file:
                alreadyProcessdWords = json.load(file)
            # do the count_words
            self.count_words(phrase)

            # take what we saved into json
            with open("./word-count.json", "r", encoding="utf-8") as file:
                newWords = json.load(file)

            # merge them
            for k, v in alreadyProcessdWords.items():
                if k in newWords:
                    newWords[k] += v
                else:
                    newWords[k] = v
            # save it into the json file
            with open("./word-count.json", "w", encoding="utf-8") as file:
                json.dump(newWords, file, ensure_ascii=False)
            # stop if next step is over the required
            if depth == 0:
                return None

        phrase_tmp = phrase.replace(" ", "_")
        if self.use_local:
            soup = siteDownloaderOffline(phrase_tmp)
        else:
            URL_tmp = self.link + "/" + phrase_tmp
            soup = siteDownloader(URL_tmp)
        # we search for hyperlinks
        div = soup.find("div", class_="mw-parser-output")
        if div is None:
            return False
        para = div.find_all("p")
        hyperlinks = []
        for paragraph in para:
            # we take the attributes
            tmp_links = paragraph.find_all("a")
            for link in tmp_links:
                # we check if is it valid wiki page
                if (
                    ("href" in link.attrs)
                    and (isItWikiPage(link["href"]))
                    and not InBanned(link["href"])
                ):
                    hyperlinks.append(extractPhrase(link["href"]))

        for hyperlink in hyperlinks:
            # if we didn't process it then we do
            if hyperlink not in self.alreadyProcessed:
                self.alreadyProcessed.add(hyperlink)
                self.auto_count_words(hyperlink, depth - 1, wait)
        return True
