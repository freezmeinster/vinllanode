from settings import Settings
from utils.server import Server,prepare_kmod
from utils.log import Logger

class Test(object):
    
    def nguk(self,val1,val2):
        return "hasil %s + %s adalah %s" % (val1, val2 , val1+val2)

server = Server()
server.hook_object(Test(),'test')
server.hook_object(Test(),'lala')
prepare_kmod()
server.run()