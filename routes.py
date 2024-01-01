from flask import Flask
from controllers.feedback import FeedbackController
from controllers.diagnosis import DiagnosisController

class Routes:

    def __init__(self, app: Flask) -> None:
        self.app = app
        self.diagnosis = DiagnosisController()
        self.feedback = FeedbackController()

    def initialize(self):
        # diagnosis api
        self.app.add_url_rule("/api/v1/diagnosis/getSummary", methods=["POST"], view_func=self.diagnosis.getDiagnosisSummary)
        self.app.add_url_rule("/api/v1/diagnosis/ask", methods=["POST"], view_func=self.diagnosis.getDiagnosisQNA)
        self.app.add_url_rule("/api/v1/qna/getAll", methods=["POST"], view_func=self.diagnosis.getAllQna)
        self.app.add_url_rule("/api/v1/qna/getById", methods=["POST"], view_func=self.diagnosis.getQnaById)

        # feedback api
        self.app.add_url_rule("/api/v1/feedback/add", methods=["POST"], view_func=self.feedback.addFeedback)
        self.app.add_url_rule("/api/v1/feedback/getAll", methods=["POST"], view_func=self.feedback.getAllFeedback)
        self.app.add_url_rule("/api/v1/feedback/getById", methods=["POST"], view_func=self.feedback.getFeedbackById)
        self.app.add_url_rule("/api/v1/feedback/edit", methods=["POST"], view_func=self.feedback.editFeedback)

