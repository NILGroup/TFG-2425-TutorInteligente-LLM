import json
import config.config as config

from orchestrator.orchestrator import Orchestrator
from .connection import Connection

import threading

def listen(connection : Connection, addr):
    LISTENER_MSG = f"LISTENER MSG ({addr[0]}:{addr[1]}):"

    print(f"{LISTENER_MSG} Client connected")
    
    orchestrator = Orchestrator()

    for i in range(2):
        threading.Thread(target=orchestrator.run, daemon=True).start()

    decoder = json.JSONDecoder()
    buffer = ''
    with connection.conn:
        while True:
            data = bytearray()
            chunk = connection.conn.recv(32768) # 2^15
            if not chunk:
                break  
            buffer += chunk.decode('utf-8')

            while buffer:
                try:
                    msg_json, index = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    break #no hay un JSON completo al principio del buffer

                orchestrator.messages.put((connection, msg_json))

                buffer = buffer[index:].lstrip()  #limpiamos el buffer y quitamos espacios del comienzo
            
    print(f"{LISTENER_MSG} Client disconnected")
    if orchestrator:
        orchestrator.report_agent.generate_report()
    return



