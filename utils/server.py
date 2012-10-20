import Pyro4
import sys
sys.path.append("..")
import subprocess
from log import Logger
from settings import Settings

class Server(object):
    def __init__(self,host=None,port=None):
        set = Settings()
        self.logger = Logger()
        if host or port == None :
            host = set.get_item('core','server_host')
            port = set.get_item('core','server_port')
        self.host = host
        self.port = port
        Pyro4.config.HMAC_KEY = set.get_item('core','hmac_phrase')
        self.daemon = Pyro4.Daemon(
            host = self.host,
            port = self.port
        )
    
    def hook_object(self,obj,id=None):
        self.logger.success("Exposing object %s" % id)
        self.uri = self.daemon.register(obj,objectId=id)
    
    def run(self):
        self.logger.success(
            "VinllaNode Object Server Successfuly run at %s:%s" %
            (self.host,self.port)
            )
        self.daemon.requestLoop()

def track_logging(fn):
    l = Logger()
    def wrapper(self, *args):
        return fn(self, *args)
    return wrapper

def execute_command(command):
    try :
        return subprocess.check_output(command,shell=True)
    except :
        return None

def prepare_kmod():
    kmod_list = []
    sets = Settings()
    l = Logger()
    for section in sets.config_parse.sections() :
        try :
            kmod_list.extend(
                sets.get_item(section,"kmod_required").split(",")
            )
        except :
            pass
            
    for kmod in kmod_list :
        l.info("Succesed load module %s" % kmod)
        if kmod :
            execute_command("modprobe %s" % kmod)
        else :
            pass
            