
enable_llm = True

max_char_per_msg = 100

previous_questions = -1

context_sensibility = 6 #Si una pregunta es valorada menor a este numero será filtrada

invalid_elems = ['floor', 'mesh', 'manager', 'variable', 'render', 'child', 'volume', 'quest', 'controller', 'player'] #Los elementos del mapa que contengan estos substrings serán ignorados

max_distance_to_player = 1000 #Los elementos del mapa cuya distancia al jugador sea superior a esta, serán ignorados