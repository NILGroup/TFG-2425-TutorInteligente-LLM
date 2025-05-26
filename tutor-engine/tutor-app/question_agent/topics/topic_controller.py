from llm.llm import ask
import json
from .topic_generator import TopicGenerator

class TopicController():
    def __init__(self, context_manager):
        self.default_topics = [
            "Saludos, presentaciones y frases básicas para iniciar una conversación",
            "Descripción de objetos y funcionamiento del entorno de realidad virtual",
            "Tareas y acciones que el usuario debe realizar para avanzar en el entorno",
            "Ubicación o localización de objetos dentro del entorno virtual",
            "Diálogos, mensajes e información proporcionada por personajes del entorno"
            ] #Topics the user may ask about
        self.ai_generated_topics = []
        self.context_manager = context_manager
        self.topic_generator = TopicGenerator(context_manager, self)
        self.format_msg = "[{'topic_index': 0, 'context': 'nuevo contexto'},...]"

    def manage_ai_topics(self):
        if len(self.ai_generated_topics) > 0:
            context = (
                "Durante una conversación, solo se permite hablar sobre ciertos temas. Algunos de ellos los gestionas tú, y otros no. "
                "Para cada uno de los temas que tú gestionas, existe un contexto asociado: este contexto es un resumen de todo lo que se ha dicho anteriormente sobre ese tema.\n\n"
                
                "Tu tarea es revisar el contexto de cada tema que gestionas y, únicamente si falta información importante, actualizarlo. "
                "En general, debes dejar el contexto tal como está. No debes reescribirlo solo para mejorar la redacción ni modificar detalles que ya están bien expresados.\n\n"
                
                "A continuación, se muestran los temas que tú manejas junto con su contexto actual:\n"
            )
        
            for i, topic in enumerate(self.ai_generated_topics):
                context += f"{i}. {topic}: {self.context_manager.ai_context_generators[i].generate()}\n"
                
            context += (
                "\nSi consideras necesario actualizar alguno de los contextos, responde únicamente con una lista de objetos JSON siguiendo este formato:\n"
                f"{self.format_msg}\n\n"
                "No devuelvas ningún texto adicional fuera del JSON. Si no es necesario cambiar nada, responde con una lista vacía: []."
            )

            answer = ask(context, "")

            answer_json = self.__validate_format(answer)

            for topic in answer_json:
                self.context_manager.ai_context_generators[topic["topic_index"]].context = topic["context"]
                print(f"El tutor a actualizado el contexto de {self.ai_generated_topics[topic['topic_index']]}: topic['context']")

        self.topic_generator.evaluate_and_add_topic()

    def __validate_format(self, answer):
        #Nos aseguramos de que el formato es correcto
        valid_format = False
        while not valid_format:
            try:
                answer_json = json.loads(answer)
                if type(answer_json) is not list:
                    raise Exception()
                valid_format = True
            except Exception:
                answer = ask("El formato esperado es: " + self.format_msg, answer)
        return answer_json

    def add_topic(self, topic):
        self.ai_generated_topics.append(topic)

    def get_allowed_topics(self):
        return self.default_topics + self.ai_generated_topics
    