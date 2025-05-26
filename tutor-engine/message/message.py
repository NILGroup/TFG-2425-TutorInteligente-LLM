from enum import Enum
from utilities.parse import convert_to_datetime

class MessageType(Enum):
    INIT_MSG = 0
    SYNC_MSG = 1
    QUESTION_MSG = 2

class Message:
    def __init__(self, msg_type, timestamp):
        self.msg_type = msg_type
        self.timestamp = convert_to_datetime(timestamp)


class InitMessage(Message):
    def __init__(self, json_msg):
        super().__init__(MessageType.INIT_MSG, json_msg['timestamp'])
        
        data = json_msg['data']

        self.steps = {}
        for step in data['steps']:
            self.steps[step['id']] = step['description']

        self.level_name = data['level']['name']
        self.level_desc = data['level']['description']
        self.npc_dialogs = data['npc_dialogs']
        self.elements_location = data['elements_location']
        self.player_pos = data['player']['position']
        self.player_orientation = data['player']['orientation']
        self.tutorial = data['tutorial']

class SyncMessage(Message):
    def __init__(self, json_msg):
        super().__init__(MessageType.SYNC_MSG, json_msg['timestamp'])
        
        data = json_msg['data']

        self.progress = data['progress']
        self.npc_dialogs = data['npc_dialogs']
        self.player_pos = data['player']['position']
        self.player_orientation = data['player']['orientation']

class QuestionMessage(Message):
    def __init__(self, json_msg):
        super().__init__(MessageType.QUESTION_MSG, json_msg['timestamp'])
        self.text = json_msg['text']

        self.sync_msg = SyncMessage(json_msg['sync'])
