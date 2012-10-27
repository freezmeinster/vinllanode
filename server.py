#!/usr/bin/env python

from settings import Settings
from utils.server import Server,prepare_kmod
from utils.log import Logger
from utils.storage import Storage
from vrm import Vrm

tank = Storage()

server = Server()
server.hook_object(tank)
prepare_kmod()
server.run()

