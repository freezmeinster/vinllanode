import sys
sys.path.append("..")
import subprocess
from log import Logger
from settings import Settings
import Pyro4


def track_logging(fn):
    l = Logger()
    def wrapper(self, *args):
        c_name = self.__class__.__name__
        l.info(
            "Executing method %s at class %s" % (fn, c_name)
        ) 
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
            
def is_ip_set(ip):
    comm = "ifconfig -a | grep -w %s" % ip
    if execute_command(comm) :
        return True
    else :
        return False

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
        if is_ip_set(self.host):
            self.daemon = Pyro4.Daemon(
                host = self.host,
                port = self.port
            )
        else :
            self.logger.critical(
                "Server can't bind to address %s Vinlla not detect this IP in Server" % self.host
            )
            sys.exit()
    
    def hook_object(self,obj,id=None):
        self.logger.success(
            "Exposing object %s in PYRO:%s@%s:%s" %
            (obj.__class__.__name__, id, self.host, self.port))
        self.uri = self.daemon.register(obj,objectId=id)
    
    def run(self):
        self.logger.success(
            "VinllaNode Object Server Successfuly run at %s" %
            (self.daemon.locationStr)
            )
        self.daemon.requestLoop()