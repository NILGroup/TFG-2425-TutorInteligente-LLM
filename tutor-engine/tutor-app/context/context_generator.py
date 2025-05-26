import config.config as config

class ContextGenerator:
    def __init__(self, knowledge, student):
        self.knowledge = knowledge
        self.student = student
        self.context = ""
    
    def generate(self):
        return self.context
    
class LevelInfoGenerator(ContextGenerator):
    def __init__(self, knowledge, student):
        super().__init__(knowledge, student)
        self.context = (
            f"Actualmente, el usuario se encuentra en un nivel denominado: '{self.knowledge.level_name}', "
            f"cuya descripción es la siguiente: '{self.knowledge.level_desc}'.\n\n"
        )
class GreetingGenerator(ContextGenerator):
    def __init__(self, knowledge, student):
        super().__init__(knowledge, student)
        self.context = (
            "El estudiante está intentando iniciar una conversación contigo. "
            "Tu respuesta debe ser cordial y agradable. Preséntate únicamente si aún no lo has hecho "
            "o si el estudiante te lo solicita de forma directa.\n\n"
        )
class VREnvironmentGenerator(ContextGenerator):
    def __init__(self, knowledge, student):
        super().__init__(knowledge, student)
        self.context = (
            "A continuación se presenta un breve tutorial con explicaciones sobre el funcionamiento "
            "del entorno de realidad virtual y sus elementos clave:\n\n"
        )

        for title, description in self.knowledge.tutorial:
            self.context += f"- {title}: {description}\n"

class TasksGenerator(ContextGenerator):
    def generate(self):
        self.context = (
            "El estudiante debe realizar en orden los siguientes pasos para completar el nivel:\n\n"
        )
        
        for i, step_key in enumerate(self.knowledge.steps.keys(), start=1):
            paso = self.knowledge.steps[step_key]
            self.context += f"{i}. {paso}:"
            
            if step_key in self.student.progress:
                instante = self.student.progress[step_key]
                self.context += f" Completado en el instante {instante}.\n"
            else:
                self.context += " Aún no completado.\n"
            
            self.context += "\n"
        
        return self.context

class PositionGenerator(ContextGenerator):
    def generate(self):
        self.context = (
        "El mapa contiene una serie de elementos ubicados en las siguientes posiciones:\n\n"
        )
        
        for elem_name, position in self.knowledge.elems_location.items():
            self.context += f"- {elem_name} se encuentra en la posición {position}.\n"
        
        self.context += (
            "\nImportante: los nombres utilizados anteriormente son identificadores internos del entorno. "
            "No debes usarlos directamente. Adáptalos siempre al lenguaje natural al comunicarte con el estudiante.\n"
        )

        _, last_pos = self.knowledge.player_positions[-1]

        self.context += (
            f"El usuario se encuentra actualmente en la siguiente posición interna: {last_pos}.\n\n"
            "Si necesitas indicarle dónde está un objeto, ten en cuenta que el usuario no comprende coordenadas numéricas.\n"
            "Nunca debes mostrarle coordenadas directamente. En su lugar, ofrece instrucciones en lenguaje natural como:\n"
            "- Sigue recto\n"
            "- Está cerca de...\n"
            "- Gira a la derecha\n"
            "- Sal de la habitación\n"
            "- Cruza la puerta que tienes enfrente\n"
        )
        self.context += "\n"
        
        return self.context

class DialogGenerator(ContextGenerator):
    def generate(self):
        self.context = "El estudiante ha recibido la siguiente información de los personajes del entorno:\n\n"

        for npc in self.student.known_npc_dialogs:
            npc_dialogs = self.knowledge.npcs[npc]
            self.context += f"- Personaje {npc}:\n"
            
            for dialog_index, (time_stamp, visible_length) in self.student.known_npc_dialogs[npc].items():
                full_dialog = npc_dialogs[int(dialog_index)]
                visible_part = full_dialog[:visible_length]
                self.context += f"  * {time_stamp}: {visible_part}\n"
        
        self.context += (
            "Los nombres utilizados para identificar a los personaje son nombres internos del sistema. "
            "El estudiante no los conoce ni debe verlos mencionados en ninguna respuesta. "
            "Siempre debes referirte a los personajes de forma natural o descriptiva, según el contenido del mensaje.\n\n"
        )

        return self.context

class PreviousChatGenerator(ContextGenerator):
    def __init__(self, knowledge, student):
        super().__init__(knowledge, student)
        self.context = (
            "A continuación se muestran las últimas preguntas realizadas por el estudiante "
            "y las respuestas que ha recibido del sistema:\n\n"
        )
        self.last_question = 0

    def generate(self):
        #Si el numero de preguntas previas a considerar es negativo, se consideran todas, sino como maximo la cantidad que se indique        
        n = len(self.student.previous_questions) if config.previous_questions < 0 else min(config.previous_questions, len(self.student.previous_questions))
        if n > 0:
            while self.last_question < n:
                timestamp, question = self.student.previous_questions[self.last_question]
                self.context += f"- Pregunta ({timestamp}): {question}\n"
                self.context += f"  Respuesta: {self.student.previous_answers[self.last_question]}\n"
                self.last_question += 1
            return self.context
        return ""

class AIGeneratedTopic(ContextGenerator):
    def __init__(self, knowledge, student, context):
        super().__init__(knowledge, student)
        self.context = context