import boto3


class DynamoDB:

    def __init__(self, regionName, accessKey, secretAccessKey):
        self.regionName = regionName
        self.accessKey = accessKey
        self.secretAccessKey = secretAccessKey
        self.dynamodb = self.createDynamodbClient()

    def createDynamodbClient(self):
        return boto3.resource(
            'dynamodb',
            region_name=self.regionName,
            aws_access_key_id=self.accessKey,
            aws_secret_access_key=self.secretAccessKey
        )

    def connectToTable(self, table):
        table = self.dynamodb.Table(table)
        return table

    def storeItem(self, tableName, item):
        table = self.connectToTable(tableName)
        table.put_item(Item=item)

    def getAllItems(self, tableName):
        table = self.connectToTable(tableName)
        response = table.scan()
        return response.get('Items', [])

    def getItemByKey(self, tableName, key):
        table = self.connectToTable(tableName)
        response = table.get_item(Key=key)
        return response.get('Item', None)

    def updateFeedback(self, tableName, feedbackId, feedback):
        table = self.connectToTable(tableName)
        update_expression = "SET #feedback = :new_feedback_status"
        expression_attribute_values = {":new_feedback_status": feedback}
        expression_attribute_names = {"#feedback": "feedback"}

        response = table.update_item(
            Key={'id': feedbackId},
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ExpressionAttributeNames=expression_attribute_names,
            ReturnValues="UPDATED_NEW"
        )

        updated_item = response.get('Attributes', None)
        return updated_item

