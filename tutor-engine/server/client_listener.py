import json
import time
import config.config as config
from its.student import Student
from its.knowledge import Knowledge
from its.tutor import Tutor
from message.message import InitMessage, QuestionMessage, SyncMessage
import unicodedata


def listen(conn, addr):
    LISTENER_MSG = f"LISTENER MSG ({addr[0]}:{addr[1]}):"
    CLIENT_MSG = f"CLIENT MSG ({addr[0]}:{addr[1]}):"
    ERROR_MSG = "ERROR MSG"

    print(f"{LISTENER_MSG} Client connected")

    student = Student()
    knowledge = Knowledge()
    tutor = Tutor(student, knowledge)

    with conn:
        while True:
            data = conn.recv(32768) # 2^15
            if not data:
                break
            
            msg_json = {}
            try:
                msg_json = json.loads(data.decode())
            except Exception:
                print(f"{ERROR_MSG} Could not parse {data.decode()} to JSON format")
                continue
            
            print(f"{CLIENT_MSG} {msg_json}")

            if msg_json['type'] == 'init':
                msg = InitMessage(msg_json)
                knowledge.setup_level(msg)
            elif msg_json['type'] == 'question':
                msg = QuestionMessage(msg_json)
                student.update(msg.sync_msg)
                if config.enable_llm:
                    answers = tutor.generate_answers(msg.text)
                else:
                    answers = ['Hola, como puedo ayudarte hoy?','¡Hola!','?Hola, este mensaje ha sido generado por el tutor?', 'Como ves, el tutor puede enviar varios mensajes']
                student.store_question(msg.text, answers)
                send(conn, answers)
            elif msg_json['type'] == 'sync':
                msg = SyncMessage(msg_json)
                student.update(msg)
            else:
                print(f"{ERROR_MSG} Invalid 'type': {msg_json} ")

    print(f"{LISTENER_MSG} Client disconnected")
    return

def send(conn, answers):
    conn.sendall(len(answers).to_bytes(4, 'little')) #Notify ADARVE the number of messages that are sent
    for ans in answers:
        time.sleep(0.05) #Necesario para que se puedan procesar los mensajes
        conn.sendall((len(ans) + count_non_ascii_characters(ans)).to_bytes(4, 'little')) #Send the message length
        time.sleep(0.05) #Necesario para que se puedan procesar los mensajes
        normalized_ans = unicodedata.normalize('NFC', ans)
        conn.sendall(normalized_ans.encode()) #Send the message
    return

def count_non_ascii_characters(text):
    return sum(1 for char in text if ord(char) >= 128)