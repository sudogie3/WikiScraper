import argparse
from .wiki_scraper_class import Scraper


def creating_parser():
    parser = argparse.ArgumentParser()
    # we are adding arguments to argparse
    parser.add_argument(
        "--summary",
        type=str,
        default=None,
        help="searching phrase")

    parser.add_argument(
        "--table",
        type=str,
        default=None,
        help="searching for a table in ..."
    )

    parser.add_argument(
        "--number",
        type=int,
        default=-1,
        help="searching for n-th table"
    )

    parser.add_argument(
        "--first-row-is-header",
        action="store_true",
        help="if this argument is given then we claim that first row is a header",
    )

    parser.add_argument(
        "--count-words",
        type=str,
        default=None,
        help="counting in given phrase words"
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
