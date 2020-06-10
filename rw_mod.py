'''Read/Write from/to xml and json classes'''

import xml.etree.ElementTree as ET
import sys 
import json

class conf_dealer:
    def __init__(self, ip = None, port = None):
        self.ip_address = ip
        self.port_number = port
    
    def save(self,filename):
        data = {"ip" : self.ip_address, "port" : self.port_number}
        with open(filename, 'w') as f:
            json.dump(data,f)

    def load(self,filename):
        with open(filename) as f:
            data = json.load(f)
        self.ip_address = data["ip"]
        self.port_number = data["port"]
        return data
    def show(self):
        print(self.ip_address)
        print(self.port_number)
    def update(self, b,c):
        self.ip_address = b
        self.port_number = c

class xml_dealer:
    def __init__(self):
        self.root = None

    def create_xml_root(self):
        self.root = ET.Element("root")
    
    def load_xml(self,filename):
        tree = ET.parse(filename)
        self.root = tree.getroot()
    
    def show_xml(self):
        for child in self.root:
            player_id = child.attrib.get("playerid")
            move = child.text
            print(f"player: {player_id} makes a move: {move}")

    def get_move(self,index):
        text = self.root[index].text.split(',')
        ax = text[0]
        dire = int(text[1])
        player = int(self.root[index].attrib.get("playerid"))
        return player,ax,dire

    def add_move(self,player, move_type):
        ET.SubElement(self.root,"mov", playerid = player).text = move_type

    def save_xml(self,filename):
        tree = ET.ElementTree(self.root)
        tree.write(filename)
    
    def add_seed(self,seed):
        self.root.set("seed", str(seed))
    def add_player_count(self,cnt):
        self.root.set("count", str(cnt))

    def get_player_count(self):
        c =  int(self.root.attrib.get("count"))
        print(c)
        return c
    def get_seed(self):
        s = int(self.root.attrib.get("seed"))
        print(s)
        return s
    def get_move_count(self):
        return len(self.root)

