import pymongo
import pdb

# Mongo db stuff
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.test_collection



#insert into db
import datetime
post = {"author": "Agustin", "text": "My first blog post!", "tags": ["mongodb", "python", "pymongo"], "date": datetime.datetime.utcnow()}
posts = db.posts
post_id = posts.insert_one(post).inserted_id

#print post_id
#print db.collection_names(include_system_collections=False)
print " "
print "a:"
print " "
print posts.find_one({"author": "Agustin"})

#for post in posts.find():
#    print post
    
print " "
print "b:"
print " "

from bson.json_util import dumps
r = posts.find()
print r
l = list(r)
print dumps(l)
print(l)

print " "
print "c:"
print " "

print posts.find_one({"uid": "ac3680"})
#l = list(r) # a list
#print l
print dumps(r)

collection.remove({})
posts.remove()
    # #CONVERT RETURN TO LIST
    # >>> r = collection.find()   # returns an object of class 'Cursor'
# Then I convert to a list

# >>> l = list(r)             # returns a 'list' of 'dict'
# here is what print(l) returns:

# >>> [{u'date': datetime.datetime(2009, 11, 10, 10, 45), u'_id': 1, u'name': u'name1', u'value': 11},{u'date': datetime.datetime(2013, 11, 10, 10, 45), u'_id': 2, u'name': u'name2', u'value': 22}]
# #then try this:

# from bson.json_util import dumps

# dumps(l)
# #this is necessary so I can return X amount of elements in the other script - configurable Schema
    
    
# #http://stackoverflow.com/questions/19674311/json-serializing-mongodb