import datetime
import pprint
import requests
import sys

from bson.json_util import dumps

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

# Globals
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'
try:
    port_num = int(sys.argv[1]) # The port number to run on is the first argument
    DBInstance = int(sys.argv[1])
except:
    port_num = int("9002")
    DBInstance = 0

# Import and initialize MongoDB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client['databaseS' + str(DBInstance)]
collection = db.test_collection
posts = db.posts

# GET .../students - returns all information for all students
@app.route('/students', methods = [GET])
def all_users():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../students/<uid> - returns all information for specified student
@app.route('/students/<uid>', methods = [GET])
def get_student(uid):
    record = get_record(uid)
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record)
    else:
        return not_found()

# GET .../students/<uid>/courses - returns enrolled courses for specified student
@app.route('/students/<uid>/courses', methods = [GET])
def get_student_courses(uid):
    record = get_record(uid)
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record["cid_list"])
    else:
        return not_found()

# POST .../students - Create a new student
# Students are forbidden to enroll in class when they are just created
@app.route('/students', methods = [POST])
def create_new_student():
    data = form_or_json()
    if 'uid' not in data:
        return "No uid provided in new student data\n", 409
    uid = data['uid']
    if get_record(uid):
        return "Resource already exists\n", 409
    posts.insert({"uid":uid})
    for k,v in data.iteritems():
        if k == "uid":
            continue
        elif k == "cid_list":
            return "You can't create a student with a pre-enrolled list of courses\n", 409
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    print posts
    payload = json.dumps({"port": port_num, "v1": "", "v2": get_student(uid), "uid": uid, "cid": "", "verb": POST})
    post_event(uid, payload)
    message = "New student(" + uid + ") created\n"
    return message, 201

# PUT .../students/<uid> - Update student field
@app.route('/students/<uid>', methods=[PUT])
def update_student(uid):
    data = form_or_json()
    for k,v in data.iteritems():
        if k == "uid":
            return "You can't update a student's UID", 409
    v1 = get_student(uid)
    for k,v in data.iteritems():
        if k == "cid_list":
            for cid in v.split(','):
                posts.update({"uid":uid},{"$push":{"cid_list": cid}})
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    payload = json.dumps({"port": port_num, "v1": v1, "v2": get_student(uid), "uid": uid, "cid": "", "verb": PUT})
    post_event(uid, payload)
    return "Updates made successfully", 200

#Add one course to student.
@app.route('/students/<uid>/courses', methods=[POST])
def add_course(uid):
    data = form_or_json()
    cid = data['cid']
    record = get_record(uid)
    if record:
        if check_course(uid, cid):
            message = "Course(" + cid + ") already exists\n"
            return message, 409
        v1 = get_student(uid)
        posts.update({"uid":uid},{"$push":{"cid_list": cid}})
        message = "Added course(" + cid + ") to student(" + uid + ")\n"
        payload = json.dumps({"port": port_num, "v1": v1, "v2": get_student(uid), "uid": uid, "cid": cid, "verb": POST})
        post_event(uid, payload)
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
        v1 = get_student(uid)
        posts.update({"uid":uid},{"$pull":{"cid_list": cid}})
        message = "Removed course(" + cid + ") from student(" + uid + ")\n"
        payload = json.dumps({"port": port_num, "v1": v1, "v2": get_student(uid), "uid": uid, "cid": cid, "verb": DELETE})
        post_event(uid, payload)
        return message, 200
    else:
        return not_found()

# DELETE .../students/<uid> - Delete a student
@app.route('/students/<uid>', methods=[DELETE])
def delete_student(uid):
    record = get_record(uid)
    if record:
        v1 = get_student(uid)
        posts.remove({"uid":uid})
        payload = json.dumps({"port": port_num, "v1": v1, "v2": "", "uid": uid, "cid": "", "verb": DELETE})
        post_event(uid, payload)
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

# Post student change event (non-GET requests) to integrator
def post_event(uid, payload):
    if do_not_forward():
        return
    url = 'http://127.0.0.1:5000/integrator/' + uid
    print "POST to integrator: " + url
    res = requests.post(url, data=payload)
    print 'response from server:', res.text

# Looks for forward: false tag from integrator requests
def do_not_forward():
    data = form_or_json()
    return True if 'forward' in data else False

# Returns a record given a UID (uni)
def get_record(uid):
    record = posts.find_one({"uid": uid})
    return record if record else 0

# Finds a course in a record given a UID (student identifier) and a CID (course identifier)
def check_course(uid, cid):
    record = posts.find_one({"uid": uid, "cid_list": cid})
    return record if record else 0

# Returns data whether from request.form or request.data
def form_or_json():
    data = request.form
    return data if data is not None else request.data

if __name__ == '__main__':
    app.run(
        debug = True,
        port = port_num
    )
