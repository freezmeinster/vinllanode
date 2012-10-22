import Pyro4

Pyro4.config.HMAC_KEY = "ilkom2012"
uri = "PYRO:Tank@192.168.0.1:9090"
obj = Pyro4.Proxy(uri)
print obj.all_tank()