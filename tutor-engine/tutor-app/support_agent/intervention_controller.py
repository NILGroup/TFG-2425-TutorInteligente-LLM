from .thresholds import Thresholds
from llm.llm import ask
from datetime import datetime
import json

class InterventionController:
    def __init__(self, knowledge, student, context_manager, init_timestamp):
        self.knowledge = knowledge
        self.student = student
        self.context_manager = context_manager
        self.thresholds = [Thresholds()]
        self.init_timestamp = init_timestamp

        self.format_msg = (
            '{\n'
            '  "Tiempo de inactividad": segundos,\n'
            '  "Preguntas fuera de contexto": numero,\n'
            '  "Permitir tareas fuera de orden": booleano,\n'
            '  "Tiempo desde la última tarea completada": segundos\n'
            '}\n\n'
        )
        pass

    def update_thresholds(self, timestamp, triggered_thresholds):
        n = len(self.thresholds)
        context = (
            "Eres un sistema inteligente encargado de ajustar dinámicamente los parámetros de intervención de un tutor "
            "en un entorno de aprendizaje en realidad virtual, enfocado en situaciones de emergencia radiológica.\n\n"

            "Tu objetivo es garantizar que el tutor intervenga en el momento justo: ni demasiado pronto "
            "(para evitar interrupciones innecesarias), ni demasiado tarde "
            "(para prevenir la frustración del estudiante).\n\n"

            "Cuando ciertos datos superan los umbrales establecidos, el tutor interviene. "
            "Tu tarea consiste en ajustar dichos umbrales según el contexto actual. A continuación, se muestran los umbrales que puedes modificar:\n"
        )

        for name, description in zip(Thresholds.names, Thresholds.descriptions):
            context += f"- {name}: {description}\n"

        context += "\nInformación relevante sobre el nivel actual:\n"
        context += self.context_manager.generate_level_info_context()

        context += f"\nContexto actual del jugador (instante {timestamp}):\n"
        context += f"- Posiciones previas del jugador: {self.knowledge.player_positions}\n"
        context += f"- Orientaciones previas del jugador (dirección de la mirada): {self.knowledge.player_orientation}\n"
        context += f"- Preguntas realizadas fuera de contexto: {self.student.out_of_context_questions}\n"

        context += self.context_manager.generate_tasks_context()

        context += self.context_manager.generate_conversation_context()

        context += (
            "Un experto fijó manualmente los siguientes valores al iniciar el nivel:\n"
            f"{Thresholds.default_thresholds_dict}\n\n"
        )


        context += "Valores anteriores de los umbrales (últimas configuraciones generadas por este sistema):\n"
        if n > 1:
            for t in self.thresholds[min(0,n-4):n-1]:
                if t.creation_timestamp is None:
                    context += f"- Experto: {t.thresholds_dict}\n"
                else:   
                    context += f"- {t.creation_timestamp}: {t.thresholds_dict}\n"
        else:
            context += "Los umbrales aún no han sido modificados.\n"

        context += f"\nValores actuales de los umbrales (instante {timestamp}):\n"
        context += f"{self.thresholds[n - 1].thresholds_dict}\n"

        if len(triggered_thresholds) > 0:
            context += "\n El tutor acaba de intervenir debido a los siguientes umbrales superados, por lo que habrás de modificarlos:\n"
            for thres_id, value, thres_value in triggered_thresholds:
                context += f"- {Thresholds.names[thres_id]}: valor actual = {value}, umbral = {thres_value} \n"

        context += (
            "\nPuedes modificar un umbral, varios o ninguno, según consideres necesario."
            "Solo debes modificar un umbral si hay una razón clara basada en el nuevo contexto del jugador." 
            "No alternes valores de forma arbitraria ni reviertas cambios recientes sin justificación."
            "Evita devolver valores diferentes si el contexto no ha cambiado significativamente."
            "Además, siempre que el tutor intervenga deberás actualizar los umbrales que se han sobrepasado, por lo menos duplicando su valor en caso de ser numéricos."
            "Por ejemplo, si un jugador supera el umbral de preguntas fuera de contexto, "
            "hay que incrementar dicho umbral para que no se le siga interrumpiendo constantemente por el mismo motivo."
            "Devuelve un JSON con los valores actualizados de los umbrales, siguiendo el formato:\n"
            f"{self.format_msg}"
            "No incluyas ningún texto adicional fuera del JSON."
            "Solo si no modificas ningún umbral, devuelve un JSON vacío, es decir, {}."
        )
        answer = ask(context, "")

        if answer != "{}":
            new_thresholds = self.validate_format(answer)
            print(f"El tutor ha actualizado los umbrales de intervención: {new_thresholds}")
            self.thresholds.append(Thresholds(new_thresholds))


    def validate_format(self, answer):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                for name in Thresholds.names:
                    if name not in answer_json:
                        raise Exception()
                valid_format = True
            except Exception:
                answer = ask("El formato esperado es: " + self.format_msg, answer)
        return answer_json
    
    def decide_intervention(self, curr_time):
        #Calcular tiempo inactividad
        triggered_thresholds = []

        last_activity = max(self.knowledge.last_movement, self.student.last_learning)
        curr_threshold = self.thresholds[-1].thresholds_dict

        thres_id = 0
        inactivity_time = (curr_time - last_activity).total_seconds()
        thres_value = int(curr_threshold[Thresholds.names[thres_id]])
        if inactivity_time > thres_value:
            triggered_thresholds.append((thres_id, inactivity_time, thres_value))

        thres_id += 1
        thres_value = int(curr_threshold[Thresholds.names[thres_id]])
        if len(self.student.out_of_context_questions) > thres_value:
            triggered_thresholds.append((thres_id, len(self.student.out_of_context_questions), thres_value))

        thres_id += 1
        thres_value = bool(curr_threshold[Thresholds.names[thres_id]])
        if self.student.out_of_order_progress != thres_value:
            triggered_thresholds.append((thres_id, self.student.out_of_order_progress, thres_value))
        
        thres_id += 1
        if len(self.student.progress) > 0:
            last_task = list(self.student.progress.keys())[-1]
            last_task_time = self.student.progress[last_task]
        else:
            last_task_time = self.init_timestamp
        time_since_last_task = (curr_time - last_task_time).total_seconds()
        thres_value = int(curr_threshold[Thresholds.names[thres_id]])
        if  time_since_last_task > thres_value:
            triggered_thresholds.append((thres_id, time_since_last_task, thres_value))

        return triggered_thresholds

