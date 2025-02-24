from flask import Flask
from flask_pymongo import pymongo
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mongo = pymongo.MongoClient(app.config['MONGO_URI'])

print(mongo)