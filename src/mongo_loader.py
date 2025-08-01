# src/mongo_loader.py

from pymongo import MongoClient

def get_all_candidates():
    client = MongoClient("mongodb+srv://candidate:aQ7hHSLV9QqvQutP@hardfiltering.awwim.mongodb.net/")
    db = client.get_database("candidates_db")  # replace with your actual DB
    collection = db.get_collection("candidates")  # replace with your actual collection
    return list(collection.find())
