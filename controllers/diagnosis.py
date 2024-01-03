from authUser import Authentication
from services.diagnosis import DiagnosisService
from flask import request, make_response, jsonify


class DiagnosisController:
    
    def __init__(self) -> None:
        self.auth = Authentication()
        self.diagnosis = DiagnosisService()

    def getDiagnosisSummary(self):
        
        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "screeningId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            if request.json["screeningId"] == "":
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            response = self.diagnosis.getDiagnosiSummary(request.json["screeningId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)
    
    def getAllDiagnosisSummary(self):
        
        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "screeningId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            if request.json["screeningId"] == "":
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            response = self.diagnosis.getAllDiagnosisSummary(request.json["screeningId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)
    
    def getDiagnosisSummaryById(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "reportId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "reportId is required"}), 400)

            if request.json["reportId"] == "":
                return make_response(jsonify({"status": 400, "message": "reportId is required"}), 400)

            response = self.diagnosis.getDiagnosisSummaryById(request.json["reportId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)


    def getDiagnosisQNA(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            keys = ["screeningId", "userQuery"]

            for key in keys:

                if key not in request.json:
                    return make_response(jsonify({"status": 400, "message": f"{key} is required"}), 400)

                if request.json[key] == "":
                    return make_response(jsonify({"status": 400, "message": f"{key} is required"}), 400)

            response = self.diagnosis.getDiagnosisQNA(request.json)
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

    def getAllQna(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "screeningId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            if request.json["screeningId"] == "":
                return make_response(jsonify({"status": 400, "message": "screeningId is required"}), 400)

            response = self.diagnosis.getAllQNA(request.json["screeningId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

    def getQnaById(self):

        resp = self.auth.authenticate(request.headers)
        if resp["status"] == 401: return make_response(jsonify(resp), 401)
        try:

            if "qnaId" not in request.json:
                return make_response(jsonify({"status": 400, "message": "qnaId is required"}), 400)

            if request.json["qnaId"] == "":
                return make_response(jsonify({"status": 400, "message": "qnaId is required"}), 400)

            response = self.diagnosis.getQnaById(request.json["qnaId"])
            return make_response(jsonify(response), response["status"])

        except Exception as e:
            return make_response(jsonify({'status': 400, 'message': str(e)}), 400)

