from authUser import Authentication
from services.feedback import FeedbackService
from flask import request, make_response, jsonify


class FeedbackController:
    
    def __init__(self) -> None:
        self.auth = Authentication()
        self.feedback = FeedbackService()

    def addFeedback(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "qnaId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "qnaId is required"}), 400)

            if request.json["qnaId"] == "":
                return make_response(jsonify({"status": 400, "message": "qnaId is required"}), 400)

            if "feedback" not in request.json:
                return make_response(jsonify({"status": 400, "message": "feedback is required"}), 400)

            if request.json["feedback"] == "":
                return make_response(jsonify({"status": 400, "message": "feedback is required"}), 400)

            response = self.feedback.addFeedback(request.json)
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

    def getAllFeedback(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            response = self.feedback.getAllFeedback()
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)
    
    def getFeedbackById(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "feedbackId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "feedbackId is required"}), 400)

            if request.json["feedbackId"] == "":
                return make_response(jsonify({"status": 400, "message": "feedbackId is required"}), 400)

            response = self.feedback.getFeedbackById(request.json["feedbackId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

    def editFeedback(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "feedbackId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "feedbackId is required"}), 400)

            if request.json["feedbackId"] == "":
                return make_response(jsonify({"status": 400, "message": "feedbackId is required"}), 400)

            if "feedback" not in request.json:
                request.json["feedback"] = 1

            response = self.feedback.editFeedback(request.json)
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

