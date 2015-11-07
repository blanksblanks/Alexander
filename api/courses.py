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
#    record = get_record(cid)
#    if record:
#        posts.update({"cid":cid},{"$push":{"uid_list": uid}})
#    else:
#        return not_found()

#def add_course(cid):
#    record = get_record(cid)
#    if record:
#        return
#    else:
#        posts.insert({"cid": cid, "uid_list": []})


# Returns a record given a CID (course identifier)
def get_record(cid):
    record = posts.find_one({"cid": cid})
    if record:
        return record
    else:
        return 0


# Finds a student in a record given a CID (course identifier) and UID (student identifier)
def check_student(cid, uid):
    record = posts.find_one({"cid": cid, "uid_list": uid})
    print record
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


# GET .../courses - returns all information for all courses
@app.route('/courses', methods = [GET])
def all_courses():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)


# GET .../courses/<cid> - returns all information for specified course
@app.route('/courses/<cid>', methods = [GET])
def get_course(cid):
    record = get_record(cid)
    if record:
        print "Found matching record for CID: ", cid
        return dumps(record)
    else:
        return not_found()


# GET .../courses/<cid>/courses - returns students for specific course
@app.route('/courses/<cid>/students', methods = [GET])
def get_course_students(cid):
    record = get_record(cid)
    if record:
        print "Found matching record for CID: ", cid
        return dumps(record["uid_list"])
    else:
        return not_found()

#Add student to course.
@app.route('/courses/<cid>/students', methods=[POST])
def add_student(cid):
    uid = request.form['uid']
    record = get_record(cid)
    if record:
        if check_student(cid, uid):
            message = "Student(" + uid + ") already exists\n"
            return message, 409
        v1 = get_course(cid)
        posts.update({"cid":cid},{"$push":{"uid_list": uid}})
        message = "Added student(" + uid + ") to course(" + cid + ")\n"
        data = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "uid": uid, "verb": POST})
        post_event(cid, data)
        return message, 200
    else:
        return not_found()
    #uid_list = posts.find({"cid": cid})
    #uid_list.append(uid)
    #print uid_list
    #print posts.find({"cid": cid})


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
        data = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "uid": uid, "verb": DELETE})
        post_event(cid, data)
        return message, 200
    else:
        return not_found()
    #posts = db.posts
    #uid_list = posts.find({"cid": cid})
    #uid_list.append(uid)

#Update course info.
# PUT .../students/<uid> - Update student field
@app.route('/students/<uid>', methods=[PUT])
def update_course(cid):
    for k,v in request.form.iteritems():
        if k == "cid":
            return "You can't update a course's CID", 409
    v1 = get_course(cid)
    for k,v in request.form.iteritems():
        if k == "uid_list":
            for uid in v.split(','):
                posts.update({"cid":cid},{"$push":{"uid_list": uid}})
        else:
            posts.update({"cid":cid},{"$set":{k:v}})
    data = json.dumps({"port": port_num, "v1" : v1, "v2": get_course(cid), "uid": "", "verb": PUT})
    post_event(cid, data)
    return "Updates made successfully", 200

#Add course to database.
@app.route('/courses', methods=[POST])
def add_course():
    cid = request.form['cid']
    record = get_record(cid)
    if record:
        message = "Course(" + cid + ") already exists\n"
        return message, 409
    posts.insert({"cid":cid})
    for k,v in request.form.iteritems():
        if k == "cid":
            continue
        elif k == "uid_list":
            # Add each course in a comma-delimited string to uid_list
            for uid in v.split(','):
                posts.update({"cid":cid},{"$push":{"uid_list": uid}})
        else:
            posts.update({"uid":uid},{"$set":{k:v}})
    data = json.dumps({"port": port_num, "v1" : "", "v2": get_course(cid), "uid": "", "verb": POST})
    message = "Course(" + cid + ") added\n"
    post_event(cid, data)
    return message, 200
    #uid_list = posts.find({"cid": cid})
    #uid_list.append(uid)
    #print uid_list
    #print posts.find({"cid": cid})

#Remove course from database.
@app.route('/courses/<cid>', methods=[DELETE])
def remove_course(cid):
    record = get_record(cid)
    if record:
        v1 = get_course(cid)
        posts.remove({"cid":cid})
        data = json.dumps({"port": port_num, "v1" : v1, "v2": "", "uid": "", "verb": DELETE})
        message = "Course(" + cid + ") removed\n"
        post_event(cid, DELETE)
        return message, 200
    else:
        return not_found()
    #uid_list = posts.find({"cid": cid})
    #uid_list.append(uid)
    #print uid_list
    #print posts.find({"cid": cid})

# Post course change event to integrator
def post_event(cid, payload):
    url = 'http://127.0.0.1:5000/integrator/' + cid
    print "POST to integrator: " + url
    res = requests.post(url, data=payload)
    print 'response from server:', res.text

#http://127.0.0.1:5000/integrator/COMS4111-3/9001/DELETE

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
    app.run(debug=True, port=port_num)
