## Courses Microservice ##

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
db = client['databaseC']
course_collection = db.test_collection
posts = db.posts

#course_collection.remove({}) # start clear
# posts.remove() # start clear

# Globals
port_num = int("9001")
GET = 'GET'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'

# GET .../courses - returns all information for all courses
@app.route('/courses', methods = [GET])
def all_courses():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../courses - returns all information for all courses
@app.route('/courses/schema/table', methods = [PUT])
def change_schema():
    data = form_or_json()
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    print l
    for each in l:
        cid = each['cid']
        for k,v in data.iteritems():
            if k != 'cid':
                posts.update({"cid":cid},{"$pull":{k:v}})
                #posts.remove({"cid":cid})
                posts.update({"cid":cid},{"$push":{k:v}})
                #posts.update({"cid":cid},{"$set":{k:v}})
    return "Schema successfully updated"
    
# GET .../courses/<cid> - returns all information for specified course
@app.route('/courses/<cid>', methods = [GET])
def get_course(cid):
    record = get_record(cid)
    if record:
        return dumps(record)
    else:
        return not_found()


# GET .../courses/<cid>/courses - returns students for specific course
@app.route('/courses/<cid>/students', methods = [GET])
def get_course_students(cid):
    record = get_record(cid)
    if record:
        return dumps(record["uid_list"])
    else:
        return not_found()

#Add student to course.
@app.route('/courses/<cid>/students', methods=[POST])
def add_student(cid):
    data = form_or_json()
    uid = data['uid']
    record = get_record(cid)
    if record:
        if check_student(cid, uid):
            message = "Student(" + uid + ") already exists\n"
            return message, 409
        v1 = get_course(cid)
        posts.update({"cid":cid},{"$push":{"uid_list": uid}})
        message = "Added student(" + uid + ") to course(" + cid + ")\n"
        payload = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "cid": cid, "uid": uid, "verb": POST})
        post_event(cid, payload)
        return message, 201
    else:
        return not_found()

#Remove student from course.
@app.route('/courses/<cid>/students/<uid>', methods=[DELETE])
def remove_student(cid, uid):
    record = get_record(cid)
    if record:
        if not check_student(cid, uid):
            message = "Student(" + uid + ") does not exist\n"
            return message, 409
        v1 = get_course(cid)
        posts.update({"cid":cid},{"$pull":{"uid_list": uid}})
        message = "Removed student(" + uid + ") from course(" + cid + ")\n"
        payload = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "cid": cid, "uid": uid, "verb": DELETE})
        post_event(cid, payload)
        return message, 200
    else:
        return not_found()

#Update course info.
@app.route('/courses/<cid>', methods=[PUT])
def update_course(cid):
    data = form_or_json()
    for k,v in data.iteritems():
        if k == "cid":
            return "You can't update a course's CID", 409
    v1 = get_course(cid)
    for k,v in data.iteritems():
        if k == "uid_list":
            uid_list = v.split(',') if v is not '' else []
            posts.update({"cid":cid},{"$set":{"uid_list": uid_list}})
        else:
            posts.update({"cid":cid},{"$set":{k:v}})
    payload = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "cid": cid, "uid": "", "verb": PUT})
    post_event(cid, payload)
    return "Updates made successfully", 200

#Add course to database.
@app.route('/courses', methods=[POST])
def add_course():
    data = form_or_json()
    if 'cid' not in data:
        return "No cid provided in new course data\n", 409
    if 'uid_list' in data:
        return "You can't create a course with a pre-existing list of students\n", 409
    record = get_record(data['cid'])
    cid = data['cid']
    if get_record(cid):
        message = "Course(" + cid + ") already exists\n"
        return message, 409
    posts.insert({"cid": cid, "uid_list": []})
    for k,v in data.iteritems():
        if k == "cid":
            continue
        else:
            posts.update({"cid":cid},{"$set":{k:v}})
    payload = json.dumps({"port": port_num, "v1" : "", "v2": get_course(cid), "cid": cid, "uid": "", "verb": POST})
    message = "Course(" + cid + ") added\n"
    post_event(cid, payload)
    return message, 201

#Remove course from database.
@app.route('/courses/<cid>', methods=[DELETE])
def remove_course(cid):
    record = get_record(cid)
    if record:
        v1 = get_course(cid)
        posts.remove({"cid":cid})
        payload = json.dumps({"port": port_num, "v1" : v1, "v2": "", "cid": cid, "uid": "", "verb": DELETE})
        message = "Course(" + cid + ") removed\n"
        post_event(cid, payload)
        return message, 200
    else:
        return not_found()

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

# Looks for forward: false tag from integrator requests
def do_not_forward():
    data = form_or_json()
    return True if 'forward' in data else False

# Returns data whether from request.form or request.data
def form_or_json():
    data = request.data
    return json.loads(data) if data is not '' else request.form

# Returns a record given a CID (course identifier)
def get_record(cid):
    record = posts.find_one({"cid": cid})
    return record if record else 0

# Finds a student in a record given a CID (course identifier) and UID (student identifier)
def check_student(cid, uid):
    record = posts.find_one({"cid": cid, "uid_list": uid})
    return record if record else 0

# Post course change event to integrator
def post_event(cid, payload):
    if do_not_forward():
        return
    url = 'http://127.0.0.1:5000/integrator/' + cid
    print "Posted to integrator: " + url
    res = requests.post(url, data=payload)
    print 'Response from integrator:', res.text

if __name__ == '__main__':
    app.run(debug=True, port=port_num)
