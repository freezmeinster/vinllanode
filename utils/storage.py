import sys
sys.path.append("..")
from utils.server import execute_command
    

class Storage(object):
    
    def __init__(self):
        self.all_pv = self.__all_physical_volume()
        self.all_lv = self.__all_logical_volume()
        self.all_disk = self.__all_disk()
    
    def get_disk_list(self):
        return self.__all_disk()
        
    def get_physical_volume_list(self):
        return self.all_pv
    
    def get_volume_group_list(self):
        return self.__all_volume_group()
    
    def get_partition_of(self,disk):
        return self.__all_partition().get(disk)
    
    def make_physical_volume(self,block):
        if "/dev/" + block in self.all_pv :
            return False
        else :
            execute_command("pvcreate /dev/%s" % block)
            return True
    
    def make_volume_group(self,pv):
        pass
    
    def make_logical_volume(self,vg,name,size):
        pass
    
    def __check_disk_on_server(self, disk):
        if disk in self.__all_disk():
            return True
        else :
            return False
    
    def __all_disk(self):
        tank_list = {}
        raw_comm = "cat /proc/partitions | grep -E -w '[s|h]d[a-z]' | awk '{ print $4 , $3}'"
        comm = execute_command(raw_comm)
        for tank in comm.strip().split("\n"):
            content = tank.split()
            tank_list[content[0]] = {
                "size" : int(content[1]) / 1024
            }
        return tank_list

    def __all_partition(self):
        part_list = {}
        for disk in self.__all_disk():
            raw_comm = "fdisk -l /dev/sda | grep -E '/dev/sda[1-9]' | awk '{ print $1, $4, $6}'"
            comm = execute_command(raw_comm)
            part = {}
            for p in comm.strip().split("\n"):
                content = p.split()
                part[content[0].split('/dev/')[1]] = {
                    "size" : int(content[1].replace('+','0')) / 1024,
                    "system" : content[2]
                }
            part_list[disk] = part
        return part_list
    
    def __all_physical_volume(self):
        command = "pvdisplay -C --units b --aligned --separator '|' \
                  --noheadings -o pv_name,pv_size,pv_used,pv_free,vg_name"
        pvs = execute_command(command)
        result = {}
        mb = 1024*1024
        for pv in pvs.split('\n'):
            if pv :
                data = pv.strip().split('|')
                total = int(data[1].split("B")[0])
                used = int(data[2].split("B")[0])
                free = int(data[3].split("B")[0])
                result[data[0].strip()] = {
                    'total_space'   : total / mb ,
                    'used_space'    : used / mb,
                    'free_space'    : free / mb,
                    'volume_group'  : data[4]
                 }
        return result
    
    def __all_logical_volume(self):
        command = "lvdisplay -C --aligned --units b --separator '|' \
                  --noheadings -o lv_name,vg_name,lv_size,lv_path"
        pvs = execute_command(command)
        result = {}
        mb = 1024*1024
        for pv in pvs.split('\n'):
            if pv :
                data = pv.strip().split('|')
                total = int(data[2].split("B")[0])
                result[data[0]] = {
                    'total_space'   : total / mb ,
                    'volume_group'  : data[1],
                    'device_path'   : data[3]
                 }
        return result
    
    def __all_volume_group(self):
        command = "vgdisplay -C --units b --noheadings  --aligned \
                  --separator '|' -o vg_name,vg_size,vg_free"
        vgs = execute_command(command)
        pv_list = self.all_pv
        result = {}
        mb = 1024*1024
        for vg in vgs.split('\n'):
            if vg :
                data = vg.strip().split('|')
                total = int(data[1].split("B")[0])
                free = int(data[2].split("B")[0])
                used = total - free
                pvs = []
                for pv in pv_list :
                    if pv_list.get(pv).get('volume_group') == data[0] :
                        pvs.append(pv)
                        
                result[data[0]] = {
                    'total_space'   : total / mb ,
                    'free_space'    : free / mb,
                    'used_space'    : used / mb,
                    'pv_list'       : pvs
                 }
        return result