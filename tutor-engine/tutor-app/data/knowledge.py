from message.message import InitMessage, SyncMessage
import config.config as config
import math
import threading

class Knowledge():
    def __init__(self):
        self._lock = threading.RLock()

        #Static knowledge
        self.level_name = ''
        self.level_desc = ''
        self.steps = {}
        self.starting_time = None
        self.npcs = {}
        self.elems_location = {}
        self.tutorial = [] #Primera posicion titulo, segunda posicion descripcion

        #Dynamic knowledge
        self.player_positions = []
        self.player_orientation = []
        self.last_movement = None

    def setup_level(self, init_msg : InitMessage):
        with self._lock:
            self.level_name = init_msg.level_name
            self.level_desc = init_msg.level_desc
            self.steps = init_msg.steps
            self.starting_time = init_msg.timestamp
            self.last_movement = init_msg.timestamp


            for npc in init_msg.npc_dialogs:
                conversations = []

                for conversation in npc['dialog']:
                    dialogs = conversation.split('@')
                    conversations.append(dialogs)
            
                self.npcs[npc['name']] = conversations
            
            for elem in init_msg.elements_location:
                if self.___is_valid_elem(elem, init_msg.player_pos):
                    pos = elem['position']
                    self.elems_location[elem['name']] = [pos['X'], pos['Y'], pos['Z']]

            self.player_positions.append((init_msg.timestamp, init_msg.player_pos))
            self.player_orientation.append((init_msg.timestamp, [init_msg.player_orientation['X'], init_msg.player_orientation['Y'], init_msg.player_orientation['Z']]))
            
            for elem in init_msg.tutorial:
                self.tutorial.append([elem['title'], elem['description']])
            


    def ___is_valid_elem(self, elem, player_pos):
        with self._lock:
            for invalid in config.invalid_elems:
                name = elem['name'].lower()
                if invalid in name:
                    return False
                
                pos = elem['position']
                
                if self.___distancia([pos['X'], pos['Y'], pos['Z']], [player_pos['X'], player_pos['Y'], player_pos['Z']]) > config.max_distance_to_player:
                    return False

            return True
    
    def ___distancia(self, punto1, punto2):
        with self._lock:
            return math.sqrt((punto2[0]-punto1[0])**2 + (punto2[1]-punto1[1])**2 + (punto2[2]-punto1[2])**2)

    def update(self, sync_msg : SyncMessage):
        with self._lock:
            self.player_positions.append((sync_msg.timestamp, sync_msg.player_pos))
            self.player_orientation.append((sync_msg.timestamp,[sync_msg.player_orientation['X'], sync_msg.player_orientation['Y'], sync_msg.player_orientation['Z']]))
            n = len(self.player_positions)
            if n >= 2 and self.player_positions[n-1][1] != self.player_positions[n-2][1]:
                self.last_movement = sync_msg.timestamp 

