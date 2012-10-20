import logging
import sys
sys.path.append("..")
from settings import Settings
from colorama import Fore, Back, Style

class Logger(object):
    
    def __init__(self):
        sets = Settings()
        logging.basicConfig(
            filename=sets.get_item('core','log_file'),
            format="%(asctime)s %(message)s",
            level=logging.DEBUG)
    
    def info(self,msg):
        logging.info(msg)
        print Fore.CYAN + msg
    
    def warning(self,msg):
        logging.warning(msg)
        print Fore.RED + msg
    
    def success(self,msg):
        logging.info(msg)
        print Fore.GREEN + msg