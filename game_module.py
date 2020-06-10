import math
import random
from os import system, name
import socket
import threading
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import time
from rw_mod import *

class field:
    def __init__(self, x, y, z, value, player_id):
        self.x = x
        self.y = y
        self.z = z
        self.v = value
        self.id = player_id
        if(self.v == 0):
            self.id = 2

    def show_field(self):
        sp = board_size-1-len(str(self.v))
        f = math.ceil(sp/2)
        e = math.floor(sp/2)

        tp = "{}{}{}".format(f*" ", str(self.v) + ","+str(self.id), e*" ")
        print("  " + tp + "  ", end="")


class board_class:
    def __init__(self, board_size):
        self.size = board_size
        self.blocks = [2**x for x in range(1, 5)]
        self.board = self.generate_board(board_size)

    def generate_board(self, board_size):
        
        board = []
        for x in range(-board_size + 1, board_size):
            if x < 0:
                range_0, range_1 = (-board_size + 1 - x, board_size)
            if x == 0:
                range_0, range_1 = (-board_size + 1, board_size)
            if x > 0:
                range_0, range_1 = (-board_size + 1, board_size - x)

            for y in range(range_0, range_1):
                z = -x-y
                board.append(field(x, y, z, 0, 2))
        return board

    def squeeze(self, row):
        change = False
        for i in range(len(row) - 1, -1, -1):
            if(row[i].v == 0):
                for j in range(i-1, -1, -1):
                    if(row[j].v != 0):
                        row[i].v = row[j].v
                        row[i].id = row[j].id
                        row[j].v = 0
                        row[j].id = 2
                        change = True
                        break
        return change

    def sum_row(self, row):
        is_change = self.squeeze(row)
        win = False
        for i in range(len(row) - 1, -1, -1):
            if(i-1 >= 0 and row[i].v == row[i-1].v and row[i].id == row[i-1].id and row[i].v != 0):
                row[i].v += row[i-1].v
                if(row[i].v == 2048):
                    win = True
                row[i-1].v = 0
                row[i-1].id = 2
                is_change = True
        self.squeeze(row)
        return is_change, win

    def random_field(self, player_id):
        free = [f for f in self.board if f.v == 0]
        try:
            chosen = random.choice(free)
        except:
            return False
        chosen.id = player_id
        chosen.v = random.choice(self.blocks)
        return True

    def show_board(self):
        cur_row = sorted(self.board, key=lambda x: x.z)
        old_z = 10
        for c in cur_row:
            if(old_z - c.z != 0):
                print("\n", end="")
                if(c.z <= 0):
                    print((self.size-1+c.x)*"    ", end="")
                else:
                    print((self.size-1-c.y)*"    ", end="")
            c.show_field()
            old_z = c.z
        print("\n")


class player:
    def __init__(self, id_):
        self.id = id_

    def make_move(self, axis, direction, board):
        change = False
        win = False
        axis_ids = {"x": "y", "y": "z", "z": "x"}
        for i in range(-board.size + 1, board.size):
            row = [e for e in board.board if getattr(e, axis) == i]
            row = sorted(row, key=lambda x: getattr(
                x, axis_ids.get(axis)), reverse=not direction == -1)
            c, w = board.sum_row(row)
            if(c):
                change = True
            if(w):
                win = True
        return change, win

board_size = 5

class game:
    def __init__(self, player_count):
        self.player_count = player_count
        self.moves = {"a": ["z", 1], "d": [
            "z", -1], "q": ["x", -1], "x": ["x", 1], "z": ["y", -1], "e": ["y", 1]}
        self.turn = 0
        self.board = board_class(board_size)
        self.players = []
        for _ in range(player_count):
            self.players.append(player(player_count))
        self.ax = "z"
        self.dire = 1
        self.board.show_board()
        self.end_game = False
        self.online = False

        # for online
        self.host_ip = None
        self.host_port = None
        self.idle_signal = None
        self.running = False
        self.xmler = xml_dealer()
        self.xmler.create_xml_root()
        self.xml_filename = "default.xml"
        self.replay = False
        self.replay_index = 0
        self.max_replay_index = 0
        self.seed = random.randint(0, 1000)
        random.seed(self.seed)
        self.xmler.add_seed(self.seed)
        self.xmler.add_player_count(self.player_count)

    def game_one_step(self):
        if(self.replay == False):
            change, win = self.players[self.turn].make_move(
                self.ax, self.dire, self.board)
            if(change == True and win == False):
                self.turn = (self.turn+1) % self.player_count
                self.board.random_field(self.turn)
                self.board.show_board()
                if(self.online == True):
                    self.send_move(f"move,{self.ax},{self.dire}")

                self.xmler.add_move(str(self.turn), f"{self.ax},{self.dire}")
                self.xmler.save_xml(self.xml_filename)
                
                print("q - up-left  || c - down-right")
                print("e - up-right || z - down-left")
                print("a - left       || d - right")
            if(win == True):
                print(f"WYGRYWA {self.turn}")
                self.end_game = True
        else:
            self.turn,self.ax,self.dire = self.xmler.get_move(self.replay_index)
            self.players[self.turn].make_move(self.ax,self.dire,self.board)
            self.board.random_field(self.turn)
            self.board.show_board()

    def connect_to_server(self, turn_sig):
        self.address = (self.host_ip, self.host_port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_turn = False
        self.running = True
        self.connect()
        self.start_thread()
        self.continued = False
        self.switch_turn = turn_sig

    def connect(self):
        self.sock.connect(self.address)
        print("Connected")

    def start_thread(self):
        self.recv_thread = threading.Thread(target=self.receiving)
        self.recv_thread.daemon = True
        self.recv_thread.start()

    def send_move(self, move):
        if(self.my_turn == True):
            msg = move
            msg = msg.encode('utf-8')
            self.sock.sendall(msg)
            self.switch_turn.emit(0)
            self.my_turn = False
    def update_seed(self,sd):
        self.seed = sd
        random.seed(sd)

    def receiving(self):
        while self.running == True:
            if(self.my_turn == False):
                data = self.sock.recv(1024)
                data = data.decode('utf-8')
                spl = data.split(",")
                if(spl[0] == "move"):
                    ax = spl[1]
                    dire = int(spl[2])
                    self.turn = (self.turn+1) % self.player_count
                    self.players[self.turn].make_move(ax, dire, self.board)

                    self.xmler.add_move(str(self.turn), f"{ax},{dire}")
                    self.xmler.save_xml(self.xml_filename)

                    self.board.random_field(self.turn)
                    self.my_turn = True
                    self.switch_turn.emit(1)
                if(spl[0] == "first"):
                    self.board.random_field(self.turn)
                    self.my_turn = True
                    self.switch_turn.emit(1)
                if(spl[0] == "second"):
                    self.board.random_field(self.turn)
                    self.switch_turn.emit(0)
                if(spl[0] == "seed"):
                    sd = int(spl[1])
                    self.xmler.add_seed(sd)
                    random.seed(sd)
                if(spl[0] == "quit"):
                    self.switch_turn.emit(2)
            else:
                self.idle_signal.emit()
