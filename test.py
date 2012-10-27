import Pyro4

Pyro4.config.HMAC_KEY = "ilkom2012"
uri = "PYRO:Storage@192.168.0.1:9090"
obj = Pyro4.Proxy(uri)
print obj.make_logical_volume('vgpool','cobavinlla','1G','httpd')