from llm.llm import ask
import json

class AnswerGenerator:
    def __init__(self):
        self.format_msg = (
            "Debes dividir tu respuesta en mensajes de un máximo de 100 caracteres cada uno "
            "y devolverlos en el siguiente formato:\n"
            "[\"respuesta1\", \"respuesta2\", ..., \"respuestan\"]\n\n"
            "Asegúrate de que cada mensaje esté entre comillas dobles y no incluyas ningún texto fuera de la lista. "
            "Además, la lista no debe contener más de 4 elementos y si son menos mejor."
        )
        pass

    def generate_answers(self, context, question):
        context += self.format_msg
        answer = ask(context, question)

        answer_json = self.validate_format(answer)

        return answer_json

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