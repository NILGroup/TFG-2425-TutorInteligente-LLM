from server.connection import Connection
from llm.llm import ask
import json

class Action:
    def __init__(self, context_manager):
        self.name = ""
        self.description = ""
        self.context_manager = context_manager
    
    def perform(self, timestamp, title, situation_description):
        pass
        
class AddReportEvent(Action):
    def __init__(self, context_manager, report_agent):
        super().__init__(context_manager)
        self.report_agent = report_agent
        self.name = "Registrar en el informe"
        self.description = (
            "Durante toda la partida eres responsable de elaborar un informe sobre el rendimiento del estudiante. "
            "Esta acción te permite registrar en dicho informe la situación actual que has detectado."
        )
    def perform(self, timestamp, title, situation_description):
        print(f"Se ha añadido un nuevo evento al informe: {situation_description}")
        self.report_agent.add_event(timestamp, title, situation_description)

class NotifyUser(Action):
    def __init__(self, context_manager, connection : Connection):
        super().__init__(context_manager)
        self.name = "Intervenir con el estudiante"
        self.description = (
            "Al ejecutar esta acción, el tutor interrumpe al estudiante apareciendo frente a él en el entorno de realidad virtual, "
            "con el objetivo de ofrecerle ayuda de forma directa. "
            "Esta acción no debe seleccionarse si ha pasado menos de un minuto desde la última vez que se escogió."
        )
        self.format_msg = (
            "Debes dividir tu respuesta en mensajes de un máximo de 100 caracteres cada uno "
            "y devolverlos en el siguiente formato:\n"
            "[\"respuesta1\", \"respuesta2\", ..., \"respuestan\"]\n\n"
            "Asegúrate de que cada mensaje esté entre comillas dobles y no incluyas ningún texto fuera de la lista. "
            "Además, la lista no debe contener más de 4 elementos y si son menos mejor."
        )
        self.connection = connection
    def perform(self, timestamp, title, situation_description):
        context = self.context_manager.generate_intro_context()
        context += self.context_manager.generate_level_info_context()
        context += self.context_manager.generate_tasks_context()
        context += self.context_manager.generate_conversation_context()
        context += (
            "\nHas decidido intervenir para hablar con el usuario debido al siguiente motivo:\n"
            f"- {title}: {situation_description}"
        )
        context += "Tu tarea es generar una respuesta para ayudar al estudiante."
        context += self.format_msg
        answer = ask(context)
        valid_answer = self.validate_format(answer)
        print(f"Intervención de Tuddy: {valid_answer}")
        self.connection.send(valid_answer)

    def validate_format(self, answer):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                if type(answer_json) is not list:
                    raise Exception()
                valid_format = True
            except Exception:
                answer = ask(self.format_msg, answer)
        return answer_json
        
