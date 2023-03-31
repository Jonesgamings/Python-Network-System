import socket
import packet
import time
import tkinter as tk

class Client:

    def __init__(self, type_) -> None:
        self.type = type_
        self.running = False
        self.authentication_code = None
        self.version = "1.0"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((ip, port))

        except Exception as e:
            print(e)

    def disconnect(self):
        disconnection_packet = packet.Packet(packet.DISCONNECTION, {packet.AUTHENTICATION_CODE: self.authentication_code})
        self.socket.send(disconnection_packet.send(self.socket.getpeername(), time.time()))

        self.running = False
        self.socket.close()

    def kicked(self):
        self.running = False
        self.socket.close()

    def activate(self):
        self.running = True

        while self.running:
            
            try:
                received_packet_bytes = self.socket.recv(2048)
                if received_packet_bytes:
                    received_pakcet = packet.Packet.receive(received_packet_bytes, self.socket.getpeername(), time.time())
                    data = received_pakcet.pakcet_data

                    if received_pakcet.type == packet.CONNECTION:
                        self.authentication_code = data[packet.AUTHENTICATION_CODE]
                        connection_packet = packet.Packet(packet.CONNECTION, {packet.AUTHENTICATION_CODE: self.authentication_code, packet.VERSION: self.version, packet.NAME: self.type})
                        self.socket.send(connection_packet.send(self.socket.getpeername(), time.time()))

                    if received_pakcet.type == packet.DISCONNECTION:
                        if data[packet.AUTHENTICATION_CODE] == self.authentication_code:
                            self.kicked()

                else:
                    self.disconnect()

            except Exception as e:
                print(e)

class ClientUI(tk.Tk):

    def __init__(self):
        super().__init__()
        self.client = Client(None)

if __name__ == "__main__":
    ip = input("IP: ")
    port = int(input("PORT: "))
    client = Client("Harry")
    client.connect(ip, port)
    client.activate()