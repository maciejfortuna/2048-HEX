import socket
import sys
import time
import random


class server_class():
    def __init__(self):
        self.all_clients = []
        self.address = ('localhost', 50001)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(self.address)
        self.turn = 0
        self.running = True

    def wait_for_connection(self):
        print("Waiting")
        self.sock.listen()
        connection, client_address = self.sock.accept()
        self.all_clients.append(connection)
        print(f"Connected: {len(self.all_clients)}/2")

    def receive(self):
        while self.running == True:
            try:
                data = self.all_clients[self.turn].recv(1024)
                self.turn = (self.turn + 1) % 2
                self.all_clients[self.turn].sendall(data)
            except:
                self.close()
  
    def enable_player(self):
        msg = "first,now"
        msg = msg.encode("utf-8")
        self.all_clients[0].sendall(msg)
        msg = "second,now"
        msg = msg.encode("utf-8")
        self.all_clients[1].sendall(msg)

    def seed_players(self):
        seed = random.randint(0, 1000)
        msg = f'seed,{seed}'
        msg = msg.encode("utf-8")
        for s in self.all_clients:
            s.sendall(msg)

    def close(self):
        self.running = False
        sys.exit()
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

main_server = server_class()
while len(main_server.all_clients) < 2:
    main_server.wait_for_connection()
print("Starting The Game")
print(main_server.all_clients   )
main_server.seed_players()
time.sleep(1)
main_server.enable_player()
main_server.receive()
