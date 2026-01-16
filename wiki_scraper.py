import argparse
import wordfreq
import requests
from bs4 import BeautifulSoup


#Musze wybrać jakiego typu ma być to wiki (kanye west , marvel , ekipa friza)

class Scraper():
    link = None
    def __init__(self , link_URL ,use_local_html_file_instead=False ):
        self.link = link_URL
        self.use_lokal = use_local_html_file_instead

    def summary(self , phrase):
        phrase_tmp = ''
        for charackter in phrase:
            if charackter == ' ':
                phrase_tmp = phrase_tmp + '_'
            else:
                phrase_tmp = phrase_tmp + charackter
        print(phrase_tmp)
        URL_tmp = URL
        while (URL_tmp[-1] != '/'):
            URL_tmp -= URL_tmp[-1]
        URL_tmp += phrase_tmp
        response = requests.get(URL_tmp)
        print(response.status_code)
        if response.status_code != 200:
            print("Błąd pobrania strony")
        soup = BeautifulSoup(response.text, 'html.parser')

        



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
    obiekt.summary('Team Rocket')
