from data.student import Student
from data.knowledge import Knowledge
from message.message import InitMessage, QuestionMessage, SyncMessage
from question_agent.question_agent import QuestionAgent
from support_agent.support_agent import SupportAgent
from report_agent.report_agent import ReportAgent
from context.context_manager import ContextManager
from server.connection import Connection
import queue

class Orchestrator:

    def __init__(self):
        self.messages = queue.Queue()

        self.student = Student() #Es un monitor
        self.knowledge = Knowledge() #Es un monitor
        self.context_manager = None
        self.question_agent = None
        self.report_agent = None
        self.support_agent = None

    def run(self):
        while True:
            conn, msg_json = self.messages.get() #El thread se duerme aquí sin consumir cpu hasta que haya algo
            try:
                self.manage_msg(conn, msg_json)
            except Exception as e:
                print(f"Error procesando mensaje: {e}")


    def manage_msg(self, connection : Connection, msg_json):
        if msg_json['type'] == 'init':
            msg = InitMessage(msg_json)
            self.knowledge.setup_level(msg)
            self.student.setup_level(msg)
            self.context_manager = ContextManager(self.knowledge, self.student)
            self.question_agent = QuestionAgent(self.knowledge, self.student, self.context_manager)
            self.report_agent = ReportAgent(self.knowledge, self.student, self.context_manager)
            self.support_agent = SupportAgent(self.knowledge, self.student, self.context_manager, msg.timestamp, self.report_agent, connection)
            print("Nivel inicializado")
        elif msg_json['type'] == 'question':
            msg = QuestionMessage(msg_json)
            self.student.update(msg.sync_msg)
            answers = self.question_agent.generate_answers(msg)
            connection.send(answers)
        elif msg_json['type'] == 'sync':
            msg = SyncMessage(msg_json)
            self.support_agent.manage_sync(msg)
        else:
            print(f"ERROR: Invalid 'type': {msg_json} ")