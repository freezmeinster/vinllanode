import sys
sys.path.append("..")
from utils.server import execute_command

class TankSegment(object):
    def __init__(self):
        pass
    
class Tank(object):
    def __init__(self):
        pass
    
    def _all_tank(self):
        tank_list = []
        raw_comm = "cat /proc/partitions | grep -E -w '[s|h]d[a-z]' | awk '{ print $4 , $3}'"
        comm = execute_command(raw_comm)
        for tank in comm.strip().split("\n"):
            content = tank.split()
            tank_list.append([content[0], int(content[1]) / 1024])
        return tank_list
    
    def __proxy_object(self):
        pass
    

class WareHouse(object):
    def __init__(self):
        pass

class Storage(object):
    def __init__(self):
        pass