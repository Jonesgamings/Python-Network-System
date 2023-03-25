import socket
import packet
import random
import time
import _thread
import tkinter as tk

class ConnectedClient:

    def __init__(self, connection, address) -> None:
        self.connection = connection
        self.address = address
        self.name = None
        self.authentication_code = None
        self.version = ""
        self.connected = True

    def set_authentication_code(self, authentication_code):
        self.authentication_code = authentication_code

    def set_name(self, name):
        self.name = name

    def set_version(self, version):
        self.version = version

    def kick_me(self, sender):
        disconnect_packet = packet.Packet(packet.DISCONNECTION, {packet.AUTHENTICATION_CODE: self.authentication_code})
        self.connected = False
        self.connection.send(disconnect_packet.send(sender, time.time()))
        self.connection.close()

    def display_text(self):
        text = f"{self.name}: {self.address}"
        return text
    
    def check_display_text(self, display_text):
        if display_text == self.display_text():
            return True
        
class Server:

    def __init__(self) -> None:
        self.connected_clients = []
        self.max_clients = 10
        self.max_byte_length = 2048
        self.version = "1.0"
        self.ui: ServerUI = None
        self.running = False

        self.port = 8000
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.id = f"{self.ip}: {self.port}"

    def generate_authentication_code(self, address):
        address_hash = hash(address)
        random_bit = random.random()
        random_int = random.randint(0, 1024)
        authentication_code = address_hash * random_bit * random_int    
        return authentication_code

    def client_connection(self, connection, address):
        authentication_code = self.generate_authentication_code(address)
        connection_packet = packet.Packet(packet.CONNECTION, {packet.AUTHENTICATION_CODE: authentication_code})
        connection.send(connection_packet.send(self.id, time.time()))
        connection_client = ConnectedClient(connection, address)
        received_connection_pakcet = False

        while self.running:
            
            if connection_client.connected:
                try:
                    received_packet_bytes = connection.recv(self.max_byte_length)
                    if received_packet_bytes:
                        received_packet = packet.Packet.receive(received_packet_bytes, self.id, time.time())
                        data = received_packet.pakcet_data

                        #CONNECTION PACKET
                        if received_packet.type == packet.CONNECTION and received_connection_pakcet == False:
                            if data[packet.AUTHENTICATION_CODE] == authentication_code:
                                connection_client.set_authentication_code(authentication_code)
                                connection_client.set_version(data[packet.VERSION])
                                connection_client.set_name(data[packet.NAME])
                                self.connected_clients.append(connection_client)
                                received_connection_pakcet = True
                                self.ui.add_connected_client(connection_client)

                        #DISCONNECTION PACKET
                        elif received_packet.type == packet.DISCONNECTION:
                            if data[packet.AUTHENTICATION_CODE] == authentication_code:
                                connection.close()
                                index = self.connected_clients.index(connection_client)
                                self.connected_clients.remove(connection_client)
                                self.ui.disconnect_client(index)
                                break

                    else:
                        self.kick_client(self.id)

                except Exception as e:
                    continue

            else:
                break
        
        connection.close()

    def send_packet_all(self, packet):
        for client in self.connected_clients:
            packet_bytes = packet.send(self.id, time.time())
            client.connection.send(packet_bytes)

    def kick_client(self, connection_client: ConnectedClient):
        connection_client.kick_me(self.id)
        self.connected_clients.remove(connection_client)

    def kick_all(self):
        for client in self.connected_clients.copy():
            client.kick_me(self.id)

        self.connected_clients.clear()

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(self.max_clients)
        self.connected_clients.clear()
        self.running = True

        while self.running:
            
            if self.running:
                try:
                    connection, address = self.socket.accept()
                    print(address, connection)
                    _thread.start_new_thread(self.client_connection, (connection, address))

                except Exception as e:
                    continue

            else:
                break

    def close(self):
        self.kick_all()
        self.running = False
        self.socket.close()
        self.socket = None
        self.ui.clear_connected()

class ServerUI(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.server = Server()
        self.server.ui = self

        self.geometry("500x500")
        self.resizable(width = False , height = False)

        self.start_button = tk.Button(self, text = "Start", command = self.start_server, width = 10)
        self.stop_button = tk.Button(self, text = "Stop", command = self.stop_server, width = 10)
        self.kick_client_button = tk.Button(self, text = "Kick", command = self.kick_client, width = 10)
        self.send_packet_button = tk.Button(self, text = "Send Packet", command = self.send_packet, width = 10)
        ip_label = tk.Label(self, text = "IP: ")
        port_label = tk.Label(self, text = "Port: ")
        max_clients_label = tk.Label(self, text = "Max Clients: ")
        self.ip_entry = tk.Entry()
        self.port_entry = tk.Entry()
        self.max_clients_entry = tk.Entry()
        self.connected_client_listbox = tk.Listbox(self, height = 22, width = 65)

        self.start_button.grid(column = 0, row = 3)
        self.stop_button.grid(column = 1, row = 3)
        self.kick_client_button.grid(column = 0, row = 5)
        self.send_packet_button.grid(column = 1, row = 5)
        ip_label.grid(column = 0, row = 0)
        port_label.grid(column = 0, row = 1)
        max_clients_label.grid(column = 0, row = 2)
        self.ip_entry.grid(column = 1, row = 0)
        self.port_entry.grid(column = 1, row = 1)
        self.max_clients_entry.grid(column = 1, row = 2)
        self.connected_client_listbox.grid(column = 0, row = 4, columnspan = 10)

        #STARTING CONFIGS
        self.title("Server")
        self.stop_button.config(relief = tk.SUNKEN, state = tk.DISABLED)
        self.start_button.config(relief = tk.RAISED, state = tk.ACTIVE)
        self.ip_entry.insert(tk.END, f"{self.server.ip}")
        self.port_entry.insert(tk.END, f"{self.server.port}")
        self.max_clients_entry.insert(tk.END, f"{self.server.max_clients}")
        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def close_window(self):
        self.server.close()
        self.destroy()

    def clear_connected(self):
        self.connected_client_listbox.delete(0, tk.END)

    def kick_client(self):
        selected_client = self.connected_client_listbox.get(self.connected_client_listbox.curselection())
        for connected_client in self.server.connected_clients:
            if connected_client.check_display_text(selected_client):
                self.server.kick_client(connected_client)
        
        self.connected_client_listbox.delete(self.connected_client_listbox.curselection())

    def disconnect_client(self, index):
        self.connected_client_listbox.delete(index)

    def send_packet(self):
        pass

    def add_connected_client(self, connected_client):
        display_text = connected_client.display_text()
        self.connected_client_listbox.insert(tk.END, display_text)

    def start_server(self):
        self.start_button.config(relief = tk.SUNKEN, state = tk.DISABLED)
        self.stop_button.config(relief = tk.RAISED, state = tk.ACTIVE)
        self.ip_entry.config(state = "readonly")
        self.port_entry.config(state = "readonly")
        self.max_clients_entry.config(state = "readonly")

        _thread.start_new_thread(self.server.start, ())

    def stop_server(self):
        self.stop_button.config(relief = tk.SUNKEN, state = tk.DISABLED)
        self.start_button.config(relief = tk.RAISED, state = tk.ACTIVE)
        self.ip_entry.config(state = "normal")
        self.port_entry.config(state = "normal")
        self.max_clients_entry.config(state = "normal")

        self.server.close()

if __name__ == "__main__":
    ui = ServerUI()
    ui.mainloop()