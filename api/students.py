import datetime
import pprint
import requests

from bson.json_util import dumps

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

# Import and initialize Mongo DB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.test_collection
posts = db.posts # DO NOT DELETE THIS LINE!!!
collection.remove({}) # start clear
posts.remove() # start clear

# Globals
port_num = int("9002")
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# POST (WILL BE REMOVED LATER
# Pre-populates DB when students.py is restarted by stat if on debug mode
post = {"firstName": "Agustin",
        "lastName": "Chanfreau",
        "uid": "ac3680",
        "email": "ac3680@columbia.edu",
        "cid_list": ["COMS123", "COMS1234", "COMS12345"],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]
        }
post_id = posts.insert_one(post).inserted_id

post = {"firstName": "Mel",
        "lastName": "Chaasdau",
        "uid": "ab3680",
        "email": "ab3680@columbia.edu",
        "cid_list": ["COMS123", "COMS1234", "COMS12345"],
        "past_cid_list": ["COMS948", "COMS94", "COMS9841"]}
post_id = posts.insert_one(post).inserted_id

# Returns a record given a UID (uni)
def getRecordForUID(uid):
    record = posts.find_one({"uid": uid})
    if record:
        return record
    else:
        return 0

# GET .../students - returns all information for all students
@app.route('/students', methods = [GET])
def all_users():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../students/<uid> - returns all information for specified student
@app.route('/students/<uid>', methods = [GET])
def api_users(uid):
    record = getRecordForUID(uid)
    if record:
        print "Found matching record for UID: ", uid
        #postEvent(uid, GET)
        return dumps(record)
    else:
        return not_found()

# GET .../students/<uid>/courses - returns enrolledCourses for specified student
@app.route('/students/<uid>/courses', methods = [GET])
def get_student_courses(uid):
    record = getRecordForUID(uid)
    if record:
        print "Found matching record for UID: ", uid
        #postEvent(uid, GET)
        return dumps(record["enrolledCourses"])
    else:
        return not_found()

# POST .../students - Create a new student
@app.route('/students', methods=[POST])
def createNewStudent():
    print "Called createNewStudent"
    print request.form
    uid = request.form['uid']
    print "uid: " + uid
    if getRecordForUID(uid):
        return "Resource already exists\n", 409
    posts.insert({"uid":uid})
    for k,v in request.form.iteritems():
        if k == "uid":
            continue
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    print posts
    #postEvent(uid, POST)
    message = "New student(" + uid + ") created\n"
    return message, 201

# PUT .../students/<uid> - Update student field
@app.route('/students/<uid>', methods=[PUT])
def updateStudent(uid):
    #fields = list of attributes
    #for attr in fields:
    #    request.args[attr]
    print "now we are updating the following uid: ", uid
    for k,v in request.form.iteritems():
        if k == "uid":
            return "You can't update a student's UID", 409
    for k,v in request.form.iteritems():
        posts.update({"uid":uid},{"$set":{k:v}})
        # call integrator once per change*
    #postEvent(uid, PUT)
    return "Updates made successfully", 200

#Add one course to student.
@app.route('/students/<uid>/courses/<cid>', methods=[PUT])
def add_course(uid, cid):
	record = get_record(uid)
	if record:
		if check_course(uid, cid):
			message = "Course(" + cid + ") already exists\n"
			return message, 409
		posts.update({"uid":uid},{"$push":{"cid_list": cid}})
		message = "Added course(" + cid + ") to student(" + uid + ")\n"
		postEvent(uid, cid, PUT)
		return message, 200
	else:
		return not_found()

# Remove one course from student.
@app.route('/students/<uid>/courses/<cid>', methods=[DELETE])
def remove_course(uid, cid):
	record = get_record(uid)
	if record:
		if not check_course(uid, cid):
			message = "Course(" + cid + ") does not exist\n"
			return message, 409
		posts.update({"uid":uid},{"$pull":{"cid_list": cid}})
		message = "Removed course(" + cid + ") from student(" + uid + ")\n"
		postEvent(uid, cid, DELETE)
		return message, 200
	else:
		return not_found()

# Returns a record given a UID (course identifier)
def get_record(uid):
    record = posts.find_one({"uid": uid})
    if record:
        return record
    else:
        return 0

# Finds a course in a record given a UID (student identifier) and a CID (course identifier)
def check_course(uid, cid):
	record = posts.find_one({"uid": uid, "cid_list": cid})
	print record
	if record:
		return record
	else:
		return 0

# DELETE .../students/<uid> - Delete a student
@app.route('/students/<uid>', methods=[DELETE])
def deleteStudent(uid):
    record = getRecordForUID(uid)
    if record:
        posts.remove({"uid":uid})
        #postEvent(uid, DELETE)
        return "Student deleted successfully", 200
    else:
        return "Not Found", 404

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

# Post student change event to integrator
def postEvent(uid, cid, action):
	post = 'http://127.0.0.1:5000/integrator/'
	if (uid): #pkey
		post += uid + "/"
	if (cid): #fkey
		post += cid + "/"
	post += str(port_num) + "/"
	post += str(action)
	print "POST to integrator: " + post
	res = requests.post(post)
	print 'response from server:', res.text

if __name__ == '__main__':
    app.run(
        debug = True,
        port = port_num
    )
