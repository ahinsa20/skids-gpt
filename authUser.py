import os
import cognitojwt


class Authentication:

    def __init__(self) -> None:
        self.region = os.getenv("AWS_REGION")
        self.userPoolId = os.getenv("COGNITO_USER_POOL_ID")
        self.clientId = os.getenv("COGNITO_USER_CLIENT_ID")

    def authenticate(self, headers):

        if "Authorization" not in headers:
            return {"status": 401, "message": "Authorization Token is required"}

        if headers["Authorization"] == "":
            return {"status": 401, "message": "Authorization Token is required"}

        try:
            cognitojwt.decode(
                token = headers["Authorization"],
                region = self.region,
                userpool_id = self.userPoolId,
                app_client_id = self.clientId,
                testmode=False
            )
            return {"status": 200}

        except Exception as e:
            return {"status": 401, "message": "You are not Authorized. Please Contact Admin"}

