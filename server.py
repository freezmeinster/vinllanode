#!/usr/bin/env python

from settings import Settings
from utils.server import Server,prepare_kmod
from utils.log import Logger
from utils.storage import Tank
from vrm import Vrm

tank = Tank()

server = Server()
server.hook_object(tank)
prepare_kmod()
server.run()

