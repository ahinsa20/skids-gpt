import os
import boto3
import pickle
import openai
import logging
from uuid import uuid4
from datetime import datetime
from json import loads, dumps
from .dynamoDb import DynamoDB
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import AzureChatOpenAI
load_dotenv()


class DiagnosisService:

    def __init__(self) -> None:

        print("dynamo db connecting .......", flush=True)
        self.db = DynamoDB(
            regionName = os.getenv("AWS_REGION"), 
            accessKey = os.getenv("AWS_ACCESS_KEY"), 
            secretAccessKey = os.getenv("AWS_SECRET_KEY")
        )
        print("dynamo db connected .......", flush=True)

        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_type = os.getenv("OPENAI_API_TYPE")
        openai.api_base = os.getenv("OPENAI_API_BASE")
        openai.api_version = os.getenv("OPENAI_API_VERSION")

        print("s3 connecting .......", flush=True)
        s3_client = boto3.client(
            's3', 
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY"), 
            aws_secret_access_key = os.getenv("AWS_SECRET_KEY")
        )
        print("s3 connected .......", flush=True)

        response = s3_client.get_object(Bucket = os.getenv("AWS_BUCKET_NAME"), Key = os.getenv("OBJECT_KEY"))
        fileBytes = response['Body'].read()

        self.chatHistory = []
        self.generalChat = []
        self.index = pickle.loads(fileBytes)
        print("embeddings load successfully......",flush=True)

        # load get summary model
        self.llm = AzureChatOpenAI(deployment_name = os.getenv("DEPLOYMENT_NAME"), openai_api_version = os.getenv("OPENAI_API_VERSION"))
        template = """provide diagnosis summary of the key information based on the following 
            report: {context} in JSON format. In the response, pragraph for overall summary with patient general information,
            pragaraph for what is normal, pragaraph for what is abnormal"""
        prompt = PromptTemplate(template=template, input_variables=["context"])
        self.__getSummary = LLMChain(llm = self.llm, prompt = prompt)

        # load model for question suggestions
        template = """based on the following diagnosis summary: {context}, give me 5 question suggestions."""
        prompt = PromptTemplate(template=template, input_variables=["context"])
        self.__questionSuggestion = LLMChain(llm = self.llm, prompt = prompt)

        # load get summary qna model
        template='''this is my child medical report {report} and general context {context} and chat history {chat_history}. I am very concerned about my child health
            and I have a question {question}, if the report has answer of the question please use report, summary and general context to answer otherwise use only context to answer. 
            The answer must be personalised and empathetic.'''
        prompt = PromptTemplate(template=template, input_variables=["report", "context", "question", "chat_history"])
        self.__getGeneralQA = LLMChain(llm = self.llm, prompt = prompt)

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

    def getDiagnosiSummary(self, screeningId):

        try:

            # file = open("./dynamoRecords/"+fileMap[screeningId], "r").read()
            queryParams = {
                'KeyConditionExpression': '#sid = :sid',
                'ExpressionAttributeNames': {
                    '#sid': 'screeningId'
                },
                'ExpressionAttributeValues': {
                    ':sid': screeningId
                }
            }
            file = self.db.getItemByKey(os.getenv("SCREENING_TABLE"), queryParams)

            if (file is None or file == []):
                return {"status": 400, "message": "report not found"}

            file = file[0]
            if isinstance(file, str):
                file = loads(file)

            file["createdAt"] = file["createdAt"].replace(".", ":")
            file["dentalAssessment"]["DMFTIndex"] = str(file["dentalAssessment"]["DMFTIndex"])

            file = self.removeKeys(file)
            docs = [Document(page_content=dumps(file))]

            answer = "Hi Parent,\n\n"
            answer += f"I am your skids-coach. I can assist you regarding {file.get('firstName', 'Patient')}'s skids report. \n\n"
            answer += "Skids assessment is the most comprehensive assessment for kids where we measure physical + behavioral + learning disabilities in children. "
            answer += "This comprehensive assessment helps to find out conditions early and in an accurate manner so that they can be cured completely,"
            answer += " and the child grows up to their full potential.\n\n"
            answer += f"I can see we need to watch out for {file.get('firstName', 'Patient')}"
            modelResponse = self.__getSummary.run({"context": docs[0].page_content}).lower()

            if "abnormal:" in modelResponse:
                abnormalIndex = modelResponse.index(" abnormal:") + len(" abnormal:")
                modelResponse = modelResponse[abnormalIndex:].strip()

            if " abnormal " in modelResponse:
                abnormalIndex = modelResponse.index(" abnormal ") + len(" abnormal ")
                modelResponse = modelResponse[abnormalIndex:].strip()

            if "abnormal " in modelResponse:
                abnormalIndex = modelResponse.index("abnormal ") + len("abnormal ")
                modelResponse = modelResponse[abnormalIndex:].strip()

            answer += modelResponse
            answer += f"You can refer to {file.get('firstName', 'Patient')}'s visual report and converse with me to explore details about the conditions.\n\n"
            answer += "I can also see you are yet to complete general assessment for you kid. You can interact me to learn how regular assessment of these \
                conditions is vital for a healthy child."

            table = self.db.connectToTable(os.getenv("SUMMARY_TABLE"))
            items = table.scan(
                FilterExpression='#screeningId = :screeningId',
                ExpressionAttributeNames={
                    '#screeningId': "screeningId"
                },
                ExpressionAttributeValues={
                    ':screeningId': screeningId
                }
            )

            if items["Items"] is not None and items["Items"] == []:
                document = {
                    "id": str(uuid4()),
                    "screeningId": screeningId,
                    "summary": answer,
                    "createdAt": str(datetime.now())
                }
                self.db.storeItem(os.getenv("SUMMARY_TABLE"), document)

            else:
                items = items["Items"][0]
                self.db.updateSummary(os.getenv("SUMMARY_TABLE"), items["id"], answer)

            questions = self.__questionSuggestion.run({"context": answer}).split("\n")
            return {"status": 200, "message": "Success", "response": {"summary": answer, "questions": questions}}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getDiagnosisQNA(self, body):

        try:

            queryParams = {
                'KeyConditionExpression': '#sid = :sid',
                'ExpressionAttributeNames': {
                    '#sid': 'screeningId'
                },
                'ExpressionAttributeValues': {
                    ':sid': body["screeningId"]
                }
            }
            file = self.db.getItemByKey(os.getenv("SCREENING_TABLE"), queryParams)
            if (file is None or file == []):
                return {"status": 400, "message": "report not found"}

            file = file[0]
            # file = open("./dynamoRecords/"+fileMap[body["screeningId"]], "r").read()
            file["createdAt"] = file["createdAt"].replace(".", ":")
            file["dentalAssessment"]["DMFTIndex"] = str(file["dentalAssessment"]["DMFTIndex"])

            docs = [Document(page_content=dumps(file))]
            response = self.index.similarity_search(body["userQuery"], k=5)
            context = ". ".join([res.page_content for res in response])

            # summary = self.db.getItemByKey(os.getenv("SUMMARY_TABLE"), {"id": body["summaryId"]})
            # if summary is None:
            #     summary = {"summary": ""}

            answer = self.__getGeneralQA.run(
                {
                    "report": docs[0].page_content,
                    # "summary": summary["summary"],
                    "context": context, 
                    "question": body["userQuery"], 
                    "chat_history": self.chatHistory
                }
            )
            questions = self.__questionSuggestion.run({"context": docs[0].page_content})

            if len(self.chatHistory) == 4:
                self.chatHistory.pop()

            self.chatHistory.append((body["userQuery"], answer))

            document = {
                "id": str(uuid4()),
                "screeningId": body["screeningId"],
                "userQuery": body["userQuery"],
                "answer": answer,
                "createdAt": str(datetime.now())
            }
            self.db.storeItem(os.getenv("QNA_TABLE"), document)

            return {"status": 200, "message": "Success", "response": {"answer": answer, "questions": questions}}

        except Exception as e:
            logging.exception(e)
            return {"status": 400, "message": str(e)}

    def getAllQNA(self, screeningId):
        try:

            # items = self.db.getAllItems(os.getenv("QNA_TABLE"))
            # items = list(filter((lambda x: x["screeningId"] == screeningId), items))

            table = self.db.connectToTable(os.getenv("QNA_TABLE"))
            items = table.scan(
                FilterExpression='#screeningId = :screeningId',
                ExpressionAttributeNames={
                    '#screeningId': "screeningId"
                },
                ExpressionAttributeValues={
                    ':screeningId': screeningId
                }
            )

            if items["Items"] is not None and items["Items"] == []:
                return {"status": 400, "message": "QNA's not found"}

            items = items["Items"]
            for index in range(len(items)):
                items[index] = self.removeKeys(items[index])

            return {"status": 200, "message": "Success", "response": items}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getQnaById(self, qnaId):
        try:

            queryParams = {
                'KeyConditionExpression': '#id = :id',
                'ExpressionAttributeNames': {
                    '#id': 'id'
                },
                'ExpressionAttributeValues': {
                    ':id': qnaId
                }
            }
            item= self.db.getItemByKey(os.getenv("QNA_TABLE"), queryParams)

            if (item is None or item == []):
                return {"status": 400, "message": "question not found"}
            
            item = item[0]
            item = self.removeKeys(item)
            return {"status": 200, "message": "Success", "response": item}

        except Exception as e:
            return {"status": 400, "message": str(e)}
    
    def getAllDiagnosisSummary(self, screeningId):
        try:

            # items = self.db.getAllItems(os.getenv("SUMMARY_TABLE"))
            # items = list(filter((lambda x: x["screeningId"] == screeningId), items))

            table = self.db.connectToTable(os.getenv("SUMMARY_TABLE"))
            items = table.scan(
                FilterExpression='#screeningId = :screeningId',
                ExpressionAttributeNames={
                    '#screeningId': "screeningId"
                },
                ExpressionAttributeValues={
                    ':screeningId': screeningId
                }
            )

            if items["Items"] is not None and items["Items"] == []:
                return {"status": 400, "message": "summary's not found"}

            items = items["Items"]

            for index in range(len(items)):
                items[index] = self.removeKeys(items[index])

            return {"status": 200, "message": "Success", "response": items}

        except Exception as e:
            return {"status": 400, "message": str(e)}

    def getDiagnosisSummaryById(self, reportId):
        try:

            queryParams = {
                'KeyConditionExpression': '#id = :id',
                'ExpressionAttributeNames': {
                    '#id': 'id'
                },
                'ExpressionAttributeValues': {
                    ':id': reportId
                }
            }
            item = self.db.getItemByKey(os.getenv("SUMMARY_TABLE"), queryParams)
            if (item is None or item == []):
                return {"status": 400, "message": "report not found"}

            item = item[0]
            item = self.removeKeys(item)
            return {"status": 200, "message": "Success", "response": item}

        except Exception as e:
            return {"status": 400, "message": str(e)}

