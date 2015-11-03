#Set courses port on 9001

#Import mongodb for python
import pymongo
import pdb

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

#Import requests and json
from bson.json_util import dumps
import requests

# Mongo db stuff
from pymongo import MongoClient
client = MongoClient() 
db = client.test_database
course_collection = db.test_collection
posts = db.posts

course_collection.remove({}) # start clear
posts.remove() # start clear

#cid = '4115'
#uid = 'wvb2103'
#posts.insert({"cid": cid, "uid_list": ['ml2138']})
#uid_list = list(posts.find({"cid": cid}))
#print uid_list
#uid_list.append(uid)
#posts.update({"cid":cid},{"$push":{"uid_list": uid}})
#uid_list = list(posts.find({"cid": cid}))
#print uid_list	
#print posts.find({"cid": cid})


#print posts.find({"cid": cid})

#posts = db.posts
#cid = '4115'
#uid = 'cd231'
#uid_list = posts.find()
#uid_list.append(uid)
#print uid_list	
#print posts.find({"cid": cid})


@app.route('/courses/addS/<cid>/<uid>')
def add_to_course(cid, uid):
	posts.update({"cid":cid},{"$push":{"uid_list": uid}})
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})


@app.route('/courses/removeS/<cid>/<uid>')
def remove_from_course(cid, uid):
	posts.update({"cid":cid},{"$pull":{"uid_list": uid}})
	#posts = db.posts
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)


@app.route('/courses/addC/<cid>')
def add_course(cid):
	posts.insert({"cid": cid, "uid_list": []})
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})


@app.route('/courses/removeC/<cid>')
def remove_course(cid):
	posts.remove({"cid":cid})
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})


#if __name__ == '__main__':
#    app.run(debug=True)
