from llm.llm import ask
import json
class TopicGenerator:
    def __init__(self, context_manager, topic_controller):
        self.context_manager = context_manager
        self.topic_controller = topic_controller
        self.format_msg = "{'topic': 'nombre del nuevo tema', 'context': 'contexto asociado al tema'}"

    def evaluate_and_add_topic(self):
        context = (
            "Un estudiante está siendo entrenado en situaciones de emergencia radiológica dentro de un entorno de realidad virtual. "
            "Durante su experiencia, puede formular pregunta a su tutor virtual, quien únicamente está autorizado a responder sobre ciertos temas predefinidos.\n"
            "El tutor dispone de un contexto específico asociado a cada uno de esos temas, que utiliza para generar respuestas cuando las preguntas son relevantes. "
            "Sin embargo, el desarrollo natural de las conversaciones puede hacer recomendable ampliar la lista de temas permitidos.\n\n"

            "Tu tarea consiste en analizar todas las conversaciones mantenidas hasta ahora y decidir si es necesario añadir un nuevo tema sobre el cual los estudiantes puedan hacer preguntas. "
            "En caso afirmativo, también deberás aportar el contexto que el tutor debe considerar cuando se le vuelva a preguntar sobre ese tema en el futuro. El contexto debe consistir en un resumen de la conversación mantenida sobre ese tema.\n"
            "A continuación, se muestra la lista actual de temas permitidos:\n"
        )

        allowed_topics = self.topic_controller.get_allowed_topics()
        for i, topic in enumerate(allowed_topics, start=1):
            context += f"{i}. {topic}\n"

        context += (
           "\nSolo debes añadir un nuevo tema si es claramente necesario, es decir, si las conversaciones incluyen preguntas "
            "relevantes y recurrentes que no encajan razonablemente en ninguno de los temas ya existentes.\n"
            "Los temas permitidos deben ser amplios y generales, no específicos o demasiado concretos. "
            "No propongas nuevos temas basados en una única pregunta aislada o en variantes menores de temas ya existentes. "
            "En general, no será necesario incluir ningún tema nuevo.\n\n"

            "Si decides añadirlo, responde exclusivamente con un JSON con el siguiente formato:\n"
            f"{self.format_msg}\n\n"

            "No des explicaciones adicionales ni justifiques tu elección.\n"
            "Si consideras que no es necesario añadir un nuevo tema, no respondas nada."
        )

        context += self.context_manager.generate_conversation_context()

        answer = ask(context,  "")

        if answer != "":
            topic, new_context = self.__validate_format(answer)
            print(f"El tutor detectó un nuevo tema: {topic}")
            print(f"Contexto: {new_context}")
            self.topic_controller.add_topic(topic)
            self.context_manager.add_topic(new_context)
        
    def __validate_format(self, answer):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                valid_format = True
            except Exception:
                answer = ask("El formato esperado es: " + self.format_msg, answer)
        return answer_json["topic"], answer_json["context"]
                    