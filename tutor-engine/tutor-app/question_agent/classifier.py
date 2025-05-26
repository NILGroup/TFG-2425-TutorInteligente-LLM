from llm.llm import ask

class Classifier:
    def __init__(self, topic_controller):
        self.topic_controller = topic_controller

    def classify(self, input):

        allowed_topics = self.topic_controller.get_allowed_topics()
        
        context = (
        "Eres un clasificador que analiza mensajes de estudiantes de emergencias radiológicas en un entorno de realidad virtual."
        "Tu tarea es identificar si el mensaje trata uno o más de los siguientes temas permitidos:\n\n"    "Lista de temas permitidos:\n"
        ) 
    
        for i, topic in enumerate(allowed_topics, start=0):
            context += f"{i}. {topic}\n"
            
        context += (
        "\nSi el mensaje comienza con un saludo seguido de contenido que no está relacionado con ningún tema permitido, "
        "no lo clasifiques como un saludo.\n"
        "Responde únicamente con los números correspondientes a los temas tratados, separados por un solo espacio.\n"
        "Ejemplo de formato de salida: 1 3 5\n\n"
        "Si el mensaje no trata sobre ningún tema de la lista, no respondas nada.\n"
        "No añadas texto, explicaciones ni comentarios. Solo responde con los números."
        )
        answer = ask(context, input, _temperature = 0)
        clasiffication = self.__split_integers(answer)
        return clasiffication


    def __split_integers(self, input_str, splitter = " "):
        if len(input_str) == 0:
            return []

        split_list = []
        str_num = ""
        try:
            for c in input_str:
                if c == splitter:
                    split_list.append(int(str_num))
                    str_num = ""
                else:
                    str_num+=c
            split_list.append(int(str_num))
        except Exception as e:
            print(e)
            return []
        
        return split_list
