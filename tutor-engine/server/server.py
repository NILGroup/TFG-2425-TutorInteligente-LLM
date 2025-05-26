import socket
import threading
from server.client_listener import listen

SERVER_MSG = "SERVER MSG:"

def start_server(ip:str, port:int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip, port))
        s.listen()
        print(f"{SERVER_MSG} Tutor listening to {ip}:{port}")
        while True:
            conn, addr = s.accept()
            listener = threading.Thread(target=listen, args=(conn, addr))
            listener.start()

    print(f"{SERVER_MSG} Server disconnected")