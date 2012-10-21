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
        print Fore.CYAN + msg + Fore.RESET
    
    def warning(self,msg):
        logging.warning(msg)
        print Fore.YELLOW + msg + Fore.RESET
    
    def success(self,msg):
        logging.info(msg)
        print Fore.GREEN + msg + Fore.RESET
        
    def critical(self,msg):
        logging.error(msg)
        print Fore.RED + msg + Fore.RESET