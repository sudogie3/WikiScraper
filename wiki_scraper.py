import argparse
import csv
import wordfreq
import requests
from bs4 import BeautifulSoup


#Musze wybrać jakiego typu ma być to wiki (kanye west , marvel , ekipa friza)

class Scraper():
    instance = None
    def __init__(self , link_URL ,use_local_html_file_instead=False ):
        self.link = link_URL
        self.use_lokal = use_local_html_file_instead

    def changingSpaceTo_(self , phrase):
        phrase_tmp = ''
        for charackter in phrase:
            if charackter == ' ':
                phrase_tmp = phrase_tmp + '_'
            else:
                phrase_tmp = phrase_tmp + charackter
        return phrase_tmp

    def SiteDownloader(self, URL):
        response = requests.get(URL)
        if response.status_code != 200:
            print(f"Nie ma takiej strony: {URL}")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def summary(self , phrase):
        phrase_tmp = self.changingSpaceTo_(phrase)
        URL_tmp = self.link + '/' + phrase_tmp
        soup = self.SiteDownloader(URL_tmp)
        para  = soup.find('p').text
        print(para)


    def table(self , phrase , number , first_row_header = False):
        phrase_tmp = self.changingSpaceTo_(phrase)
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
        for row in rows:
            dataAndHeadersInRow = row.find_all(['td' , 'th']) # dane i nagłówki
            dataAndHeadersInRowText = [data.get_text().strip() for data in dataAndHeadersInRow] # bierzemy jedynie tekst
                                                                                      # z każdej komorki
            data.append(dataAndHeadersInRowText)
        print(data)

        # with open(file_name , 'w' , encoding='utf-8') as csvfile:
        #     writer = csv.writer(csvfile)
        #     for row in rows:
        #         writer.writerow(row)







        



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
    URL = 'https://bulbapedia.bulbagarden.net/wiki'
    obiekt = Scraper(URL)
    obiekt.table('Type' , 2)
