from message.message import SyncMessage

class Student():
    def __init__(self):
        self.progress = {}
        self.known_npc_dialogs = {}
        self.out_of_context_questions = 0
        self.previous_questions = []
        self.previous_answers = []
        self.last_question = -1

    def update(self, sync_msg : SyncMessage):
        for step in sync_msg.progress:
            if step not in self.progress:
                self.progress[step] = sync_msg.timestamp
        
        for npc in sync_msg.npc_dialogs:
            if npc['name'] not in self.known_npc_dialogs:
                self.known_npc_dialogs[npc['name']] = {}

            if (npc['conversation_index'] not in self.known_npc_dialogs[npc['name']] and npc['is_talking'] is True) or npc['conversation_index'] in self.known_npc_dialogs[npc['name']]:
                self.known_npc_dialogs[npc['name']][npc['conversation_index']] = npc['dialog_index']

    def store_question(self, question: str, answer : str):
        self.previous_questions.append(question)
        self.previous_answers.append(" ".join(answer))
