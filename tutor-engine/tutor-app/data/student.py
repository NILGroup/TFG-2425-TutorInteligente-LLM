from message.message import SyncMessage, InitMessage
import threading

class Student():
    def __init__(self):
        self._lock = threading.RLock()

        self.progress = {}
        self.out_of_order_progress = False
        self.known_npc_dialogs = {}
        self.previous_questions = [] #Solo guardamos preguntas que no están fuera de contexto
        self.previous_answers = []
        self.out_of_context_questions = []
        self.out_of_context_answers = []
        self.last_question = -1
        self.last_learning = None

    def setup_level(self, init_msg : InitMessage):
        with self._lock:
            self.last_learning = init_msg.timestamp


    def update(self, sync_msg : SyncMessage):
        with self._lock:
            for step in sync_msg.progress:
                if step not in self.progress:
                    if len(self.progress) > 0:
                        last_step = list(self.progress.keys())[-1]
                        if step < last_step:
                            self.out_of_order_progress = True
                    self.progress[step] = sync_msg.timestamp
                    self.last_learning = sync_msg.timestamp
                    
            
            for npc in sync_msg.npc_dialogs:
                if npc['name'] not in self.known_npc_dialogs:
                    self.known_npc_dialogs[npc['name']] = {}

                known_conversations = self.known_npc_dialogs[npc['name']]
                conv_index = npc["conversation_index"]
                dialog_index = npc["dialog_index"]

                if conv_index not in known_conversations:
                    if npc["is_talking"]:
                        known_conversations[conv_index] = (sync_msg.timestamp, dialog_index)
                        self.last_learning = sync_msg.timestamp
                else:
                    _, existing_index = known_conversations[conv_index]
                    if dialog_index >= existing_index:
                        known_conversations[conv_index] = (sync_msg.timestamp, dialog_index)
                        self.last_learning = sync_msg.timestamp

    def store_question(self, question: str, answer : str, timestamp):
        with self._lock:
            self.last_learning = timestamp
            self.previous_questions.append((timestamp, question))
            self.previous_answers.append(" ".join(answer))

    def store_out_of_context_question(self, question: str, answer : str, timestamp):
        with self._lock:
            self.last_learning = timestamp
            self.out_of_context_questions.append((timestamp, question))
            self.out_of_context_answers.append(" ".join(answer))
