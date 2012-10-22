import sys
sys.path.append("..")
import subprocess
from log import Logger
from settings import Settings
import Pyro4
from Pyro4.core import log, MessageFactory
from Pyro4 import errors, util


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
        l.info("[OperatingSystem] Succesed load kernel module %s" % kmod)
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

class VinllaDaemon(Pyro4.Daemon):
    """
    Vinlla Daemon is modified version of Pyro Daemon.i only add some logging step
    """
    def _set_log(self,kind,msg):
        log = Logger()
        if kind == "info":
            log.info(msg)
        elif kind == "critical":
            log.critical(msg)
            
    def handleRequest(self, conn):
        """
        Handle incoming Pyro request. Catches any exception that may occur and
        wraps it in a reply to the calling side, as to not make this server side loop
        terminate due to exceptions caused by remote invocations.
        """
        flags=0
        seq=0
        wasBatched=False
        isCallback=False
        try:
            msgType, flags, seq, data = MessageFactory.getMessage(conn, MessageFactory.MSG_INVOKE)
            objId, method, vargs, kwargs=self.serializer.deserialize(
                                           data, compressed=flags & MessageFactory.FLAGS_COMPRESSED)
            del data  # invite GC to collect the object, don't wait for out-of-scope
            obj=self.objectsById.get(objId)
            if obj is not None:
                self._set_log(
                    "info",
                    "[Object] Client %s contacting object %s" %
                    (conn.sock.getpeername()[0], objId)
                )
                if kwargs and sys.version_info<(2, 6, 5) and os.name!="java":
                    # Python before 2.6.5 doesn't accept unicode keyword arguments
                    kwargs = dict((str(k), kwargs[k]) for k in kwargs)
                if flags & MessageFactory.FLAGS_BATCH:
                    # batched method calls, loop over them all and collect all results
                    data=[]
                    for method,vargs,kwargs in vargs:
                        method=util.resolveDottedAttribute(obj, method, Pyro4.config.DOTTEDNAMES)
                        try:
                            result=method(*vargs, **kwargs)   # this is the actual method call to the Pyro object
                        except Exception:
                            xt,xv=sys.exc_info()[0:2]
                            xv._pyroTraceback=util.formatTraceback(detailed=Pyro4.config.DETAILED_TRACEBACK)
                            if sys.platform=="cli":
                                fixIronPythonExceptionForPickle(xv, True)  # piggyback attributes
                            data.append(_ExceptionWrapper(xv))
                            break   # stop processing the rest of the batch
                        else:
                            data.append(result)
                    wasBatched=True
                else:
                    # normal single method call
                    method=util.resolveDottedAttribute(obj, method, Pyro4.config.DOTTEDNAMES)
                    if flags & MessageFactory.FLAGS_ONEWAY and Pyro4.config.ONEWAY_THREADED:
                        # oneway call to be run inside its own thread
                        thread=threadutil.Thread(target=method, args=vargs, kwargs=kwargs)
                        thread.setDaemon(True)
                        thread.start()
                    else:
                        isCallback=getattr(method, "_pyroCallback", False)
                        data=method(*vargs, **kwargs)   # this is the actual method call to the Pyro object
            else:
                self._set_log(
                    "critical",
                    "[Object] Client %s contacting unknown object %s" %
                    (conn.sock.getpeername()[0], objId)
                )
                raise errors.DaemonError("unknown object")
                
            if flags & MessageFactory.FLAGS_ONEWAY:
                return   # oneway call, don't send a response
            else:
                data, compressed=self.serializer.serialize(data, compress=Pyro4.config.COMPRESSION)
                flags=0
                if compressed:
                    flags |= MessageFactory.FLAGS_COMPRESSED
                if wasBatched:
                    flags |= MessageFactory.FLAGS_BATCH
                msg=MessageFactory.createMessage(MessageFactory.MSG_RESULT, data, flags, seq)
                del data
                conn.send(msg)
        except Exception:
            xt,xv=sys.exc_info()[0:2]
            if xt is not errors.ConnectionClosedError:
                if not flags & MessageFactory.FLAGS_ONEWAY:
                    tblines=util.formatTraceback(detailed=Pyro4.config.DETAILED_TRACEBACK)
                    self._sendExceptionResponse(conn, seq, xv, tblines)
            if isCallback or isinstance(xv, (errors.CommunicationError, errors.SecurityError)):
                raise

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
            self.daemon = VinllaDaemon(
                host = self.host,
                port = self.port
            )
        else :
            self.logger.critical(
                "[Server] Server can't bind to address %s, Vinlla not detect this IP belonging this Server" % self.host
            )
            sys.exit()
    
    def hook_object(self,obj,id=None):
        if id == None :
            id = obj.__class__.__name__
            
        self.logger.success(
            "[Object] Exposing object %s in PYRO:%s@%s:%s" %
            (obj.__class__.__name__, id, self.host, self.port))
        self.uri = self.daemon.register(obj,objectId=id)
    
    def run(self):
        self.logger.success(
            "[Server] VinllaNode Object Server successfuly run at %s" %
            (self.daemon.locationStr)
            )
        self.daemon.requestLoop()