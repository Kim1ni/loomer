from pymongo import MongoClient

from shared.consts import MONGODB_URI

client = MongoClient(MONGODB_URI)

db = client["loom_db"]