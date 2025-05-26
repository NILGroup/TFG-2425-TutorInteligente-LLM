from .classifier import Classifier
from .answer_generator import AnswerGenerator
from .topics.topic_controller import TopicController
import threading
class QuestionAgent:
    def __init__(self, knowledge, student, context_manager):
        self.knowledge = knowledge
        self.student = student
        self.context_manager = context_manager
        self.topic_controller = TopicController(self.context_manager)
        self.classifier = Classifier(self.topic_controller)
        self.answer_generator = AnswerGenerator()
        
    def generate_answers(self, question_message):
        classification = self.classifier.classify(question_message.text)
        context = self.context_manager.generate_context_question(classification)
        answer = self.answer_generator.generate_answers(context, question_message.text)
        
        #Update the tutor in a new thread to give a fast answer to the user
        threading.Thread(target=self.update_tutor, args=(question_message,classification,answer), daemon=True).start()
        return answer
    
    def update_tutor(self, question_message, classification, answer):
        if len(classification) > 0:
            self.student.store_question(question_message.text, answer, question_message.timestamp)
        else:
            self.student.store_out_of_context_question(question_message.text, answer, question_message.timestamp)

        self.topic_controller.manage_ai_topics()