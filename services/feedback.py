import os
from uuid import uuid4
from datetime import datetime
from .dynamoDb import DynamoDB
from dotenv import load_dotenv
load_dotenv()


class FeedbackService:

    def __init__(self) -> None:

        self.db = DynamoDB(
            regionName = os.getenv("AWS_REGION"), 
            accessKey = os.getenv("AWS_ACCESS_KEY"), 
            secretAccessKey = os.getenv("AWS_SECRET_KEY")
        )

    def removeKeys(self, obj):

        if isinstance(obj, dict):
            newObj = {}
            for key, value in obj.items():
                if key == "M":
                    newObj.update(self.removeKeys(value))
                elif key == "L":
                    newObj = self.removeKeys(value)
                elif key in ["S", "BOOL", "NULL", "N"]:
                    newObj = value
                else:
                    newObj[key] = self.removeKeys(value)
            return newObj

        elif isinstance(obj, list):
            return [self.removeKeys(item) for item in obj]

        else:
            return obj

    def addFeedback(self, body):
        try:
            
            document = {
                "id": str(uuid4()).replace("-",""),
                "qnaId": body["qnaId"],
                "feedback": body["feedback"],
                "createdAt": str(datetime.now())
            }
            self.db.storeItem(os.getenv("FEEDBACK_TABLE"), document)
            return {"status": 200, "message": "Success"}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getAllFeedback(self):
        try:

            items = self.db.getAllItems(os.getenv("FEEDBACK_TABLE"))

            for index in range(len(items)):
                items[index] = self.removeKeys(items[index])

            return {"status": 200, "message": "Success", "response": items}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getFeedbackById(self, feedbackId):
        try:

            item = self.db.getItemByKey(os.getenv("FEEDBACK_TABLE"), {'id': feedbackId})
            print(item)
            item = self.removeKeys(item)
            return {"status": 200, "message": "Success", "response": item}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def editFeedback(self, body):
        try:

            self.db.updateFeedback(os.getenv("FEEDBACK_TABLE"), body["feedbackId"], body["feedback"])
            return {"status": 200, "message": "Success"}

        except Exception as e:
            return {"status": 400, "message": str(e)}
