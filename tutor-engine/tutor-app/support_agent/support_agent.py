from .intervention_controller import InterventionController
from message.message import SyncMessage
from .action_manager import ActionManager
from server.connection import Connection

class SupportAgent():

    def __init__(self, knowledge, student, context_manager, init_timestamp, report_agent, connection : Connection):
        self.knowledge = knowledge
        self.student = student
        self.context_manager = context_manager
        self.intervention_controller = InterventionController(self.knowledge, self.student, self.context_manager, init_timestamp)
        self.action_manager = ActionManager(report_agent, connection, self.context_manager)

    def manage_sync(self, sync_msg : SyncMessage):
        self.student.update(sync_msg)
        self.knowledge.update(sync_msg)
        triggered_thresholds = self.intervention_controller.decide_intervention(sync_msg.timestamp)
        if len(triggered_thresholds) > 0:
            self.action_manager.choose_and_perfom_actions(triggered_thresholds, sync_msg.timestamp)
        self.intervention_controller.update_thresholds(sync_msg.timestamp, triggered_thresholds)
        