import Pyro4


Pyro4.config.HMAC_KEY = "ilkom2012"
uri = "PYRO:lala@192.168.0.1:9090"
obj = Pyro4.Proxy(uri)
print obj.nguk(2,4)