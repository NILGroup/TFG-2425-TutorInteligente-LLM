import threading
import unicodedata
import time

class Connection:
    def __init__(self, conn):
        self.conn = conn
        self._lock = threading.Lock() #Para proteger la conexion


    def send(self, answers):
        with self._lock:
            self.conn.sendall(len(answers).to_bytes(4, 'little')) #Notify ADARVE the number of messages that are sent
            for ans in answers:
                time.sleep(0.05) #Necesario para que se puedan procesar los mensajes
                self.conn.sendall((len(ans) + self.count_non_ascii_characters(ans)).to_bytes(4, 'little')) #Send the message length
                time.sleep(0.05) #Necesario para que se puedan procesar los mensajes
                normalized_ans = unicodedata.normalize('NFC', ans)
                self.conn.sendall(normalized_ans.encode()) #Send the message
            time.sleep(0.05) #Necesario para que se puedan procesar los mensajes
            return

    def count_non_ascii_characters(self, text):
        return sum(1 for char in text if ord(char) >= 128)