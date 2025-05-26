from .context_generator import GreetingGenerator, VREnvironmentGenerator, TasksGenerator, PositionGenerator, DialogGenerator, PreviousChatGenerator, LevelInfoGenerator, AIGeneratedTopic

class ContextManager:
    def __init__(self, knowledge, student):
        self.knowledge = knowledge
        self.student = student
        self.topic_context_generators = []
        self.topic_context_generators.append(GreetingGenerator(knowledge, student))
        self.topic_context_generators.append(VREnvironmentGenerator(knowledge, student))
        self.topic_context_generators.append(TasksGenerator(knowledge, student))
        self.topic_context_generators.append(PositionGenerator(knowledge, student))
        self.topic_context_generators.append(DialogGenerator(knowledge, student))

        self.previous_chat_generator = PreviousChatGenerator(knowledge, student)
        self.level_info_generator = LevelInfoGenerator(knowledge, student)

        self.ai_context_generators = []

        self.introduction_msg = (
            "Eres Tuddy, el tutor virtual de un agente de seguridad que está realizando su entrenamiento "
            "en un entorno de realidad virtual, llamado ADARVE, diseñado para simular situaciones de emergencia radiológica cotidianas.\n\n"
        )

    def generate_context_question(self, topics):
        context = self.introduction_msg

        context += self.level_info_generator.generate()

        if len(topics) == 0:
            context += (
                "La pregunta del usuario no está relacionada con el contenido del nivel actual. "
                "Indícaselo de forma amable y respetuosa, sin hacer que se sienta corregido."
            )

        n = len(self.topic_context_generators)
        for topic in topics:
            if topic < n:
                context += self.topic_context_generators[topic].generate()
            else:
                context += self.ai_context_generators[topic - n].generate()

        context += self.previous_chat_generator.generate()

        return context

    def generate_conversation_context(self):
        return self.previous_chat_generator.generate()
    
    def add_topic(self, context):
        self.ai_context_generators.append(AIGeneratedTopic(self.knowledge, self.student, context))

    def generate_tasks_context(self):
        return self.topic_context_generators[2].generate()
    
    def generate_level_info_context(self):
        return self.level_info_generator.generate()
    
    def generate_intro_context(self):
        return self.introduction_msg
        