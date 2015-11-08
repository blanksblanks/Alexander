# Import and initialize MongoDB
import pymongo
from pymongo import MongoClient
client = MongoClient()

#This script does three things:

# 1. Clear all databases being used:
db = client['databaseC']
collection = db.test_collection
posts = db.posts
collection.remove({})
posts.remove()

db = client['databaseS9003']
collection = db.test_collection
posts = db.posts
collection.remove({})
posts.remove()

db = client['databaseS9004']
collection = db.test_collection
posts = db.posts
collection.remove({})
posts.remove()

db = client['databaseS9005']
collection = db.test_collection
posts = db.posts
collection.remove({})
posts.remove()

db = client['databaseS0']
collection = db.test_collection
posts = db.posts
collection.remove({})
posts.remove()

# 2. Create 9 posts in databaseS0 (students database):
post = {"first_name": "Agustin",
        "last_name": "Chanfreau",
        "uid": "ac3680",
        "email": "ac3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Bob",
        "last_name": "Smith",
        "uid": "bs3680",
        "email": "bs3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Chris",
        "last_name": "Wakings",
        "uid": "cw3680",
        "email": "cw3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Gob",
        "last_name": "Smith",
        "uid": "gs3680",
        "email": "gs3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Hob",
        "last_name": "Smith",
        "uid": "hs3680",
        "email": "hs3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Tob",
        "last_name": "Smith",
        "uid": "ts3680",
        "email": "ts3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Uman",
        "last_name": "Smith",
        "uid": "us3680",
        "email": "us3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "William",
        "last_name": "Smith",
        "uid": "ws3680",
        "email": "ws3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"first_name": "Zed",
        "last_name": "Smith",
        "uid": "zs3680",
        "email": "zs3680@columbia.edu",
        "cid_list": [],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

for post in posts.find():
    print post, ">>>>>>>>>>> Now present at Students default database: databaseS0"
    
# 3. Create 4 courses in databaseC (courses database):
db = client['databaseC']
collection = db.test_collection
posts = db.posts

post = {"cid": "COMS4798",
        "uid_list": []
        }
post_id = posts.insert_one(post).inserted_id

post = {"cid": "COMS5799",
        "uid_list": []
        }
post_id = posts.insert_one(post).inserted_id

post = {"cid": "COMS6800",
        "uid_list": []
        }
post_id = posts.insert_one(post).inserted_id

post = {"cid": "COMS6802",
        "uid_list": []
        }
post_id = posts.insert_one(post).inserted_id

for post in posts.find():
    print post, ">>>>>>>>>>> Now present at Courses database"