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

    def getAllFeedback(self, qnaId):
        try:

            items = self.db.getAllItems(os.getenv("FEEDBACK_TABLE"))
            items = list(filter((lambda x: x["qnaId"] == qnaId if "qnaId" in x else x), items))

            for index in range(len(items)):
                print(items[index], flush=True)
                items[index]["feedback"] = str(items[index]["feedback"])
                items[index] = self.removeKeys(items[index])

            return {"status": 200, "message": "Success", "response": items}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getFeedbackById(self, feedbackId):
        try:

            queryParams = {
                'KeyConditionExpression': '#id = :id',
                'ExpressionAttributeNames': {
                    '#id': 'id'
                },
                'ExpressionAttributeValues': {
                    ':id': feedbackId
                }
            }

            item = self.db.getItemByKey(os.getenv("FEEDBACK_TABLE"), queryParams)
            
            if (item is None or item == []):
                return {"status": 400, "message": "feedback not found"}

            item = item[0]
            item = self.removeKeys(item)
            item["feedback"] = str(item["feedback"])
            return {"status": 200, "message": "Success", "response": item}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def editFeedback(self, body):
        try:

            self.db.updateFeedback(os.getenv("FEEDBACK_TABLE"), body["feedbackId"], body["feedback"])
            return {"status": 200, "message": "Success"}

        except Exception as e:
            return {"status": 400, "message": str(e)}
