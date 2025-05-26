from .thresholds import Thresholds
from .action import AddReportEvent, NotifyUser
from llm.llm import ask
from server.connection import Connection
import json

class ActionManager:
    def __init__(self, report_agent, connection : Connection, context_manager):
        self.actions =  [AddReportEvent(context_manager, report_agent), NotifyUser(context_manager, connection)]
        self.actions_history = [] #3-uplas en el formato (timestamp, acciones, umbrales)
        self.format_msg = "Ejemplo de formato: {actions: [0, 2], title='titulo que resuma la situacion' description='descripción de la situacion actual'}"
        

    def choose_action(self, triggered_thresholds, timestamp):
        context = (
            "Eres el tutor de un entorno de realidad virtual centrado en emergencias radiológicas. "
            "Has detectado que el alumno presenta señales de desorientación, y debes valorar la relevancia de la situación para decidir qué acciones tomar.\n\n"
            
            "El alumno ha superado los siguientes umbrales:\n"
        )

        
        for thres_id, value, thres_value in triggered_thresholds:
            context += (
                f"- {Thresholds.names[thres_id]}: {Thresholds.descriptions[thres_id]}\n"
                f"  * Valor actual: {value}\n"
                f"  * Umbral establecido: {thres_value}\n"
            )

        context += "\nLas acciones disponibles son:\n"

        for i, action in enumerate(self.actions):
            context += f"{i}. {action.name}: {action.description}\n"

        context += (
            f"\nActualmente nos encontramos en el instante {timestamp}."
            "Las últimas acciones que has tomado son:\n"
        )

        if len(self.actions_history) > 0:
            for act_timestamp, actions, thresholds in self.actions_history:
                context += f"- Intante {act_timestamp}:\n"
                
                context += "  * Acciones ejecutadas:\n"
                for act in actions:
                    context += f"    + {self.actions[act].name}\n"
                
                context += "  * Umbrales superados que motivaron la acción:\n"
                for thres_id, value, thres_value in thresholds:
                    context += (
                        f"    + {Thresholds.names[thres_id]}: Valor en el instante = {value}, Umbral en el instante: {thres_value}\n"
                    )
        else:
            context += "Aún no se ha tomado ninguna acción.\n"

        context += (
            "\nDebes seleccionar al menos una acción. "
            "Puedes realizar varias si lo consideras necesario. "
            "Devuelve únicamente un JSON que contenga:\n"
            "- Una lista con los identificadores de las acciones a ejecutar.\n"
            "- Un breve título sobre la situación actual"
            "- Una breve descripción de la situación actual. Describe objetivamente lo que está ocurriendo e indica las acciones que has tomado.\n\n"
            f"{self.format_msg}"
        )

        answer = ask(context)

        answer_json = self.validate_format(answer)

        return answer_json
        
    def choose_and_perfom_actions(self, triggered_thresholds, timestamp):
        response = self.choose_action(triggered_thresholds, timestamp)
        actions = response["actions"]
        title = response["title"]
        description = response["description"]
        self.actions_history.append((timestamp, actions, triggered_thresholds))
        for action_id in actions:
            self.actions[action_id].perform(timestamp, title, description)

    def validate_format(self, answer):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                if "actions" not in answer_json:
                    raise Exception()
                if type(answer_json["actions"]) is not list:
                    raise Exception()
                if "description" not in answer_json:
                    raise Exception()
                valid_format = True
            except Exception:
                answer = ask("El formato esperado es: " + self.format_msg, answer)
        return answer_json