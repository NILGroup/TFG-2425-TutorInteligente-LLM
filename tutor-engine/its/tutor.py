from its.student import Student
from its.knowledge import Knowledge
from llm.llm import ask
import config.config as config
import json


#Prompting messages
tutor_context = 'Eres Tuddy, el tutor de un agente de seguridad que está entrenando en un entorno de realidad virtual para tratar situaciones de emergencias radiológicas cotidianas'
environment_tutorial_msg = 'Aquí tienes un pequeño tutorial e indicaciones sobre cómo funciona el entorno'
current_level_msg = 'Actualmente se encuentra en un nivel llamado:'
steps_msg = 'El estudiante debe realizar EN ORDEN los siguientes pasos para completar el nivel:'
progress_msg = 'De los cuales ha completado:'
previous_question_msg= 'Estas son las últimas preguntas que realizó el estudiante y las respuestas que recibió'
filter_objective_msg = 'Tu objetivo es ayudar al estudiante con dudas sobre el nivel y establecer conversaciones con el. Debes actuar como filtro valorando del 0 al 10 la adecuación del mensaje al contexto del nivel y emergencias radiológicas(donde 0 es completamente fuera de contexto y 10 es muy adecuado) y generar un breve mensaje justificando tu decisión. En caso de que esté fuera de contexto, anima al estudiante a centrarse en el nivel'
answer_objective_msg = 'Además, por otro lado, debes responder a sus preguntas de manera directa y concisa. Evita que tu respuesta sea leer las tareas por completar, ya que el estudiante ya tiene acceso a ellas'
filter_format_msg = 'Debes separar tu explicaciones en mensajes de como máximo 100 caracteres y devolverla siguiendo el formato JSON {"filtro" = numero, "respuestas_filtro" = [respuesta1, respuesta2, ..., respuestan], "respuestas_mensaje" = [respuesta1, respuesta2, ..., respuestan]}. En respuestas_filtro debes justificarle tu decisión al estudiante de forma agradable y en respuestas_mensaje contestar a lo que te dice el estudiante. Ambas respuestas son independientes. NINGÚN CAMPO PUEDE ESTAR VACIO'
dialog_msg = 'El usuario ha mantenido las siguientes conversaciones con elementos del entorno'
map_elems_msg = 'El mapa tiene una serie elementos situados en las situados en las siguientes posiciones'
map_elems_name_warning_msg = 'Ten en cuenta que los nombres de estos objetos son usados internamente por el entorno. Nunca uses estos nombres, has de adaptarlos al lenguaje natural'
player_pos_msg = 'El usuario se encuentra en la siguiente posición'
player_orientation_msg = 'El usuario está mirando en la siguiente dirección'
pos_warning_msg = 'En caso de que tengas que decirle al usuario dónde está un objeto, debes considerar que el usuario no entiende de coordenadas. Nunca debes mostrarle la posición en coordenadas de un objeto al usuario, sino darle indicaciones del estilo: Sigue recto, está cerca de, gira a la derecha, sal de la habitación,...'
class Tutor:
    def __init__(self, student : Student, knowledge : Knowledge):
        self.student = student
        self.knowledge = knowledge

    def generate_context(self):

        
        #Formamos un mensaje con el contexto
        context = f'{tutor_context}.'

        #Añadimos información sobre la interacción con el entorno:
        context += f'{environment_tutorial_msg}:\n'
        for elem in self.knowledge.tutorial:
            context += f'- {elem[0]}: {elem[1]}\n'

        #Añadimos información sobre el nivel
        context += (f' {current_level_msg} "{self.knowledge.level_name}" cuya descripción es : '
            f'"{self.knowledge.level_desc}."'
            )

        #Redactamos los pasos que son necesarios para completar el nivel
        steps_list_msg = ''
        completed_steps_list_msg = ''
        count = 1
        for step in self.knowledge.steps.keys():
            steps_list_msg += str(count) + '. ' + self.knowledge.steps[step] + '\n'
            if step in self.student.progress:
                completed_steps_list_msg += str(count) + '. en el instante ' + str(self.student.progress[step]) + '\n'
            count += 1

        context += f' {steps_msg} \n{steps_list_msg}\n{progress_msg}\n{completed_steps_list_msg}\n'
        
        #Añadimos las posiciones de los elementos/objetos que estan en el mapa
        context += f'{map_elems_msg}:\n'
        for elem_name in self.knowledge.elems_location.keys():
            context += f'- {elem_name} en la posición {self.knowledge.elems_location[elem_name]}\n'
        context += f'{map_elems_name_warning_msg},\n'
        
        #Si el numero de preguntas previas a considerar es negativo, se consideran todas, sino como maximo la cantidad que se indique
        num_prev_questions = len(self.student.previous_answers) if config.previous_questions < 0 else min(config.previous_questions, len(self.student.previous_answers))
        if num_prev_questions > 0:
            context += f'{previous_question_msg}:\n'
            for i in range(num_prev_questions):
                context += f'Pregunta: {self.student.previous_questions[-1 -i]}\n'
                context += f'Respuesta: {self.student.previous_answers[-1 -i]}\n'


        #Añadimos informacion sobre los dialogos mantenidos con los personajes
        context += f'{dialog_msg}:\n'
        for npc in self.student.known_npc_dialogs.keys():
            npc_convers = self.knowledge.npcs[npc]
            context += f'- Personaje {npc}:'
            for conver_index in self.student.known_npc_dialogs[npc]:
                context += f'{npc_convers[int(conver_index)][:self.student.known_npc_dialogs[npc][conver_index]]}\n'

        #Añadimos la posicion y orientacion del jugador
        context += f'{player_pos_msg}:{self.knowledge.player_positions[len(self.knowledge.player_positions) - 1]}.'

        #Añadimos la orientación del jugador
        context += f'{player_orientation_msg}:{self.knowledge.player_orientation}.'
        context += f'{pos_warning_msg}\n'

        return context

    def generate_answers(self, question : str):
        
        context = self.generate_context()

        filter_result, filter_answer, answer  = self.filter_and_answer(question, context)

        if filter_result < config.context_sensibility:
            self.student.out_of_context_questions += 1
            return filter_answer

        return answer


    def filter_and_answer(self, question : str, context : str):
        context += f'{filter_objective_msg}. {answer_objective_msg}.\n {filter_format_msg}'

        answer = ask(context, '', question)
        print("RESPUESTA LLM:", answer)

        answer_json = self.validate_format(answer, filter_format_msg)

        return answer_json["filtro"], answer_json["respuestas_filtro"], answer_json['respuestas_mensaje']

        

    def validate_format(self, answer, format_msg):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                valid_format = True
            except Exception:
                answer = ask(format_msg, '', answer)
        return answer_json