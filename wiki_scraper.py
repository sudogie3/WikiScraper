import argparse
import csv
import json
import time
from itertools import count
from pickle import FALSE
from pydoc import replace

import numpy as np
import wordfreq
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


# Musze wybrać jakiego typu ma być to wiki (kanye west , marvel , ekipa friza)

class Scraper():

    def __init__(self , link_URL ,use_local_html_file_instead=False):
        self.link = link_URL
        self.use_lokal = use_local_html_file_instead

    def SiteDownloader(self, URL):
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Nie ma takiej strony: {URL} lub nie działa")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def summary(self , phrase):
        phrase_tmp = phrase.replace(" " , "_")
        URL_tmp = self.link + '/' + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        # zrobić to w div class
        para  = soup.find('p').get_text()
        print(para)


    def table(self , phrase , number , first_row_header = False):
        phrase_tmp = phrase.replace(" " , "_")
        URL_tmp = self.link + '/' + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        file_name = f'{phrase_tmp}.csv'
        tables = soup.find_all('table')
        if number > len(tables):
            print(f"Na stronie {URL_tmp} nie ma tylu tabel")
            return None

        table = tables[number - 1]
        rows = table.find_all('tr') # wiersze
        data = []
        print(rows)
        tableForPandas = []
        for row in rows:
            dataAndHeadersInRow = row.find_all(['td' , 'th']) # dane i nagłówki
            dataAndHeadersInRowText = [data.get_text().strip() for data in dataAndHeadersInRow] # bierzemy jedynie tekst
                                                                                     # z każdej komorki
            print(dataAndHeadersInRow)
            tableForPandas.append(pd.Series(dataAndHeadersInRowText))
            data.append(dataAndHeadersInRowText)
        #print(tableForPandas)

    def count_words(self , phrase): # done
        phrase_tmp = self.changingSpaceTo_(phrase)
        soup = self.SiteDownloader(self.link + '/' + phrase_tmp)

        if soup is None:
            return
        text = soup.find("div" , class_ = "mw-content-ltr mw-parser-output").get_text(strip=True , separator=" ")

        words = []
        word = ""
        for letter in text:
            if letter == " ":
                words.append(word)
                word = ""
            elif letter.isalpha() or letter == "-":
                word += letter.lower()

        #deleting hyperlinks
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
        with open("./word-count.json" , "w"  , encoding="utf-8") as file:
            json.dump(setOfWords ,file, ensure_ascii=False)
        return True


    def analyze_relative_word_freq(self, phrase , mode , count , chart = None):
        if not self.count_words(phrase):
            return False
        with open("./word-count.json" , "r" , encoding="utf-8") as file:
            siteData = json.load(file)
        phrase_tmp = phrase.replace(" " , "_")
        response = requests.get(self.link + '/' + phrase_tmp)
        language = response.headers.get("Content-Language")
        setFrequencyLang = {}
        setFrequencyArticle = {}
        sumWords = 0
        mostFrequencyLang = wordfreq.word_frequency(wordfreq.top_n_list(n = 1 , lang= language)[0] , language)

        for word in siteData:
            setFrequencyLang[word] = wordfreq.word_frequency(word , lang = language)/mostFrequencyLang
            sumWords += siteData[word]
        mostFrequencyArticle = max(siteData.values()) /sumWords

        for word in siteData:
            setFrequencyArticle[word] = (siteData[word]/sumWords)/mostFrequencyArticle

        df1 = pd.DataFrame(
            {
            "word": setFrequencyLang.keys() ,
            "frequency in wiki language": setFrequencyLang.values()
             }
        )
        df2 = pd.DataFrame(
            {
            "word": setFrequencyArticle.keys() ,
            "frequency in article": setFrequencyArticle.values()
             }
        )
        pd.set_option('display.float_format', '{:.4f}'.format) # wyswietlaj w zmiennoprzecinkowej , nie w naukowej

        df = pd.merge(
            df1,
            df2,
            on="word",
            how="inner"
        )

        if mode == "article":
            df = df.sort_values("frequency in article" , ascending=False)
        if mode == "language":
            df = df.sort_values("frequency in wiki language" , ascending=False)

        print(df)
        df = df.head(count)
        if chart is None:
            return None

        df.set_index("word")[["frequency in article", "frequency in wiki language"]].plot(
            kind="bar",
            figsize=(10, 5)
        )
        plt.ylabel("Frequency")
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(chart)
        return None

    def help_auto_count_words(self, phrase, depth, wait, alreadyProcessed):
        print(f"Jestem {phrase} i glębokość to {depth}")

        with open("./word-count.json" , "r", encoding='utf-8') as file:
            alreadyProcessdWords = json.load(file)


        time.sleep(wait) # zasypiamy na wait sekund

        self.count_words(phrase)
        with open("./word-count.json", "r", encoding='utf-8') as file:
            newWords = json.load(file)

        #merguje je
        for k, v in alreadyProcessdWords.items():
            if k in newWords:
                newWords[k] += v  # dodajemy wartości
            else:
                newWords[k] = v  # jeśli klucz nowy, dodajemy

        with open("./word-count.json" , "w" , encoding='utf-8') as file:
            json.dump(newWords ,file , ensure_ascii=False)
        print(newWords['the'])
        if depth == 0:
            return

        soup = self.SiteDownloader(self.link + "/" + phrase)

        para = soup.find_all('p')
        hyperlinks = []
        for paragraph in para:
            tmp_link = paragraph.find('a')
            if (tmp_link and ('href' in tmp_link.attrs) and
                    (len(tmp_link['href']) >= 6) and (tmp_link['href'][:6] == "/wiki/")):
                hyperlinks.append(tmp_link['href'][6:])


        for hyperlink in hyperlinks:
            if hyperlink not in alreadyProcessed:
                alreadyProcessed.append(hyperlink)
                self.help_auto_count_words(hyperlink, depth - 1, wait, alreadyProcessed)


    def auto_count_words(self , phrase , depth , wait):
        # szukamy hyperlączy
        soup = self.SiteDownloader(self.link + "/" + phrase)

        para = soup.find_all('p')
        hyperlinks = []
        for paragraph in para:
            tmp_link = paragraph.find('a')
            if (tmp_link and ('href' in tmp_link.attrs) and
                    (len(tmp_link['href']) >= 6) and (tmp_link['href'][:6] == "/wiki/")):
                hyperlinks.append(tmp_link['href'][6:])

        self.count_words(phrase)
        alreadyProcessed = []
        for hyperlink in hyperlinks:
            if hyperlink not in alreadyProcessed:
                alreadyProcessed.append(hyperlink)
                self.help_auto_count_words(hyperlink , depth - 1 , wait , alreadyProcessed)

def creating_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary' , type = str , help ='searching phrase')
    # parser.add_argument('--table' , type = str , help = 'searching for a table in ...')
    # parser.add_argument('--number' , type = int , help = 'searching for n-th table')
    # parser.add_argument('--first-row-is-header' , type = bool , action=False , help = 'if this argument '
    #                                                                                   'is given then we claim that first '
    #                                                                                   'row is a header')
    # parser.add_argument('--count-words' , type = str ,help = 'counting in given phrase words' )
    # parser.add_argument('--analyze-relative-word-frequency' , type = bool , help = 'shows the difference'
    #                                                                                ' between frequencies in the words '
    #                                                                                'in article' )
    # parser.add_argument('--mode' , type = str , help = 'sorts the relative-word-frequencies table by '
    #                                                    'the given arg')
    # parser.add_argument('--chart' , type = str , action=False , help= 'creates a chart of the '
    #                                                                   'relative-word-frequency analiz')
    # parser.add_argument('--auto-count-words' , type = str , help='counting in given phrase '
    #                                                              'words and going into hyperlinks')

    return parser


if __name__ == '__main__':
    URL = 'https://bulbapedia.bulbagarden.net/wiki' #to jest scrapper tej wiki
    obiekt = Scraper(URL)



