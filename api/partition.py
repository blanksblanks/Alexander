import pickle

# Import and initialize MongoDB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['databaseS0']
collection = db.test_collection
posts = db.posts

# Find out which DB instance the record goes to based on the first letter of the UID:
def getDBInstance(startsWith):
    with open('config', 'rb') as handle:
        b = pickle.loads(handle.read())
        return b[startsWith]

# Route items in the main database (client['databaseS0']) to the three other databases,
# depending on the first letter of the item's UID:
for post in posts.find():
    startsWith = post["uid"][0]
    DBInstance = getDBInstance(startsWith)
    db = client['databaseS' + str(DBInstance)]
    collection = db.test_collection
    posts = db.posts
    post_id = posts.insert_one(post).inserted_id
    
# Print out each of the three new databases (optional):
db = client['databaseS9003']
collection = db.test_collection
posts = db.posts
for post in posts.find():
    print post, "--------1"
    
db = client['databaseS9004']
collection = db.test_collection
posts = db.posts
for post in posts.find():
    print post, "--------2"
    
db = client['databaseS9005']
collection = db.test_collection
posts = db.posts
for post in posts.find():
    print post, "--------3"