from flask import Flask
from flask_pymongo import pymongo
from config import Config
from flask_cors import CORS
from datetime import timedelta




app = Flask(__name__)
CORS(app, supports_credentials=True)  # Enable CORS for all routes
app.config.from_object(Config)
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)  # Keep session for 1 day
app.config["SESSION_COOKIE_SAMESITE"] = "None"  # Required for cross-origin requests
app.config["SESSION_COOKIE_SECURE"] = True  # Required for SameSite=None


mongo = pymongo.MongoClient(app.config['MONGO_URI'])

print(mongo)