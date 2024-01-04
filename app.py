from flask import Flask
from routes import Routes
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

v1 = Routes(app)
v1.initialize()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=2000)
 
 