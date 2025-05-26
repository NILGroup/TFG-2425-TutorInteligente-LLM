from message.message import InitMessage
import config.config as config
import math

class Knowledge():
    def __init__(self):
        self.level_name = ''
        self.level_desc = ''
        self.steps = {}
        self.starting_time = None
        self.npcs = {}
        self.elems_location = {}
        self.player_positions = []
        self.player_orientation = []
        self.tutorial = [] #Primera posicion titulo, segunda posicion descripcion

    def setup_level(self, init_msg : InitMessage):
        self.level_name = init_msg.level_name
        self.level_desc = init_msg.level_desc
        self.steps = init_msg.steps
        self.starting_time = init_msg.timestamp


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

        self.player_positions.append(init_msg.player_pos)
        self.player_orientation = [init_msg.player_orientation['X'], init_msg.player_orientation['Y'], init_msg.player_orientation['Z']]
        
        for elem in init_msg.tutorial:
            self.tutorial.append([elem['title'], elem['description']])



    def ___is_valid_elem(self, elem, player_pos):
        for invalid in config.invalid_elems:
            name = elem['name'].lower()
            if invalid in name:
                return False
            
            pos = elem['position']
            
            if self.___distancia([pos['X'], pos['Y'], pos['Z']], [player_pos['X'], player_pos['Y'], player_pos['Z']]) > config.max_distance_to_player:
                return False

        return True
    
    def ___distancia(self, punto1, punto2):
        return math.sqrt((punto2[0]-punto1[0])**2 + (punto2[1]-punto1[1])**2 + (punto2[2]-punto1[2])**2)


