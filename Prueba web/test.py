from pymongo import MongoClient
import datetime

client = MongoClient()

db = client.IOT
collection = db.eventos

ev2 = {"Name": "Mike",
       "Description": "enseñandole a mati",
       "Date": datetime.datetime.utcnow(),
       "Topic": "IOT",
       "Value": "selser gay"}
post_id = db.eventos.insert_one(ev2).inserted_id
print(post_id)
