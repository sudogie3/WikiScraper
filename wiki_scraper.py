from  WikiClasses.wiki_arg_parser import Control

""" This is the main usage """
if __name__ == "__main__":
    URL = "https://bulbapedia.bulbagarden.net/wiki"
    controler = Control(URL)
    controler.iterateArguments()