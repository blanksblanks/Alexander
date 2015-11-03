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

# Globals
port_num = int("9001")
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


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

#cid1 = '4115'
#cid2 = '4111'
#uid1 = 'wvb2103'
#uid2 = 'mlh2198'
#add_course(cid1)
#add_student(cid1, uid1)
#add_course(cid2)
#add_student(cid2, uid2)
#uid_list1 = list(posts.find({"cid": cid1}))
#print uid_list1	
#uid_list2 = list(posts.find({"cid": cid2}))
#print uid_list2	

#def add_student(cid, uid):
#	record = get_record(cid)
#	if record:
#		posts.update({"cid":cid},{"$push":{"uid_list": uid}})
#	else:
#		return not_found()
	
#def add_course(cid):
#	record = get_record(cid)
#	if record:
#		return
#	else:
#		posts.insert({"cid": cid, "uid_list": []})


# Returns a record given a CID (course identifier)
def get_record(cid):
    record = posts.find_one({"cid": cid})
    if record:
        return record
    else:
        return 0


# Handle nonexistent routes
@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404
    return resp


#Add student to course.
@app.route('/courses/add/student/<cid>/<uid>', methods=[PUT])
def add_student(cid, uid):
	record = get_record(cid)
	if record:
		posts.update({"cid":cid},{"$push":{"uid_list": uid}})
	else:
		return not_found()
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})


#Remove student from course.
@app.route('/courses/remove/student/<cid>/<uid>')
def remove_student(cid, uid, methods=[DELETE]):
	record = get_record(cid)
	if record:
		posts.update({"cid":cid},{"$pull":{"uid_list": uid}})
	else:
		return not_found()
	#posts = db.posts
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)


#Add course to database.
@app.route('/courses/add/course/<cid>', methods=[POST])
def add_course(cid):
	record = get_record(cid)
	if record:
		return "Course already exists.\n", 409
	else:
		posts.insert({"cid": cid, "uid_list": []})
		return "Course added.\n", 200
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})


#Remove course from database.
@app.route('/courses/remove/course/<cid>')
def remove_course(cid, methods=[DELETE]):
	record = get_record(cid)
	if record:
		posts.remove({"cid":cid})
	else:
		return not_found()
	#uid_list = posts.find({"cid": cid})
	#uid_list.append(uid)
	#print uid_list	
	#print posts.find({"cid": cid})

# Post course change event to integrator
def postEvent(cid, method):
    res = requests.post('http://127.0.0.1:5000/integrator/' + str(port_num) + '/' + cid + '/' + method)
    print 'response from server:', res.text


#To test the methods
#cid1 = '4115'
#cid2 = '4111'
#uid1 = 'wvb2103'
#uid2 = 'mlh2198'
#add_course(cid1)
#add_student(cid1, uid1)
#add_course(cid2)
#add_student(cid2, uid2)
#uid_list1 = list(posts.find({"cid": cid1}))
#print uid_list1	
#uid_list2 = list(posts.find({"cid": cid2}))
#print uid_list2	


if __name__ == '__main__':
    app.run(debug=True)
