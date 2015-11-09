# The integrator micro-service
# It logs every transaction but will not always inform the other MS about the changes

# *: do not tell other MS about this (the change will not affect them)
# It is essential that each MS, including partitions, has its own distinct port

import os
import sys
import datetime
import pprint
import thread
import pdb
import re

from bson.json_util import dumps
import requests

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

#python integrator.py <courseMS_URL> <courseMS_port> <number of student partitions> (for each student partition,
#        list the following:) <studentMS_URL> <studentMS_port>
#ex. python integrator.py http://localhost:9001 9001 1 http://localhost:9002 9002
#ex. python integrator.py http://localhost:9001 9001 3 students http://localhost:9003 9003 http://localhost:9004 9004 http://localhost:9005 9005

courses = None
courses_port = None
students = {} # dictionary of studentsURL: studentsPort
host = "http://127.0.0.1:1235/"
ok_put_post_response = [200, 201]
ok_delete_response = [200, 404]
ok_delete_from_collection_response = [200, 409]

def main(argv):
    if (len(argv) < 5):
        print "Too few command-line arguments."
        sys.exit(1)

    ports = []
    expected_unique_ports = 0

    global courses
    courses = argv[0]

    global courses_port
    courses_port = argv[1]

    # Check to make sure courses_port is an integer and a valid port
    if (not isinstance(int(courses_port), int) or int(courses_port) < 1024):
        print "argv[1] must be a valid port"
        sys.exit(1)

    ports.append(courses_port)
    expected_unique_ports += 1

    number_of_partitions = int(argv[2])
    arg_number = 3

    global students
    for i in range(number_of_partitions):
        if (not isinstance(int(argv[arg_number+1]), int) or int(argv[arg_number+1]) < 1024):
            print "argv[" + str(arg_number+1) + "] must be a valid port"
            sys.exit(1)
        students[argv[arg_number]] = argv[arg_number+1]
        ports.append(argv[arg_number+1])
        arg_number += 2
        expected_unique_ports += 1

    # ensure that the ports are all distinct!
    if (len(set(ports)) < expected_unique_ports):
        print "Each port number must be distinct (including partitions)."
        sys.exit(1)
    app.run(debug=True)

# Check that the requester's port belongs to courses or one of the students micro-services
def check_port(port):
    if (int(port) == int(courses_port)):
        return True
    for k, v in students.iteritems():
        if int(port) == int(v):
            return True
    return False

# Creates response to return to the user
def response(data, code):
    js = json.dumps(data)
    resp = Response(js, status = code, mimetype='application/json')
    return resp

# Log message format: <timestamp> <requester IP> [<pkeys>] [<fkeys>] [<original non-primary key>] [<changed non-primary key>] <CRUD operation>
# Leave any given array as empty parentheses if there aren't any
def write_to_log(message):
    with open("log.txt", "a") as myfile:
        myfile.write(message + "\n")

def delete_from_log(timestamp):
    # Read all the lines
    f = open("log.txt", "r")
    lines = f.readlines()
    f.close()

    # Look for the line to delete
    line_number = 1
    for l in lines:
        if timestamp in l:
            break
        line_number += 1

    # Write all lines except for the one to delete into a new file
    line_count = 1
    message = ""
    n = open("newlog.txt", "a")
    for line in lines:
        if line_count != line_number:
            n.write(line)
        else:
            message += line
        line_count += 1
    n.close()
    if (len(message) > 0):
        os.rename("newlog.txt", "log.txt")
    return message

# Method to help split the key and prepare it in the correct format for the log
def format_key(key):
    substring = " ["
    key = key.replace("_", " ")
    for i in range(len(key)):
        substring += key[i]
    substring += "]"
    return substring

# POST with primary key only (primary keys are cid or uid)
# The integrator will inform the other MS about these changes
@app.route('/integrator/<primary_key>', methods = ['POST'])
def handle_event(primary_key):
    data = json.loads(request.data) #convert data into dictionary
    requester_port = data["port"]
    if (requester_port is None):
        data = {'error': 'No port specified'}
        return response(data, 400)

    # figure out who the sender was
    for k, v in data.iteritems():
        if k == 'port':
            port = int(v)
            if (port == int(courses_port)):
                sender = 'courses'
                receiver = 'students'
            else:
                for k, v in students.iteritems():
                    if port == int(v):
                        sender = 'students'
                        receiver = 'courses'
        elif k == 'verb':
            action = str(v)
        elif k == 'uid':
            uid = str(v)
        elif k == 'cid':
            cid = str(v)
        elif k == 'v1':
            old_record = v
        elif k == 'v2':
            new_record = v
    print "old record: " + old_record
    print "new record: " + new_record

    # figure out the sender's action
    if action == 'POST':
        if len(old_record) < 1: # record creation, don't need to tell other MS
            print "new record creation"
            if sender is 'students':
                print "student added: " + uid
            else:
                print "course added: " + cid
        else: # record update
            print "record update"
            if sender is 'students':
                # student added a class, tell courses MS
                print "Students added " + str(uid) + " to class " + str(cid)
                # url = host + "/courses/" + cid + "/students"
                url = get_url(receiver, cid, sender)
                payload = json.dumps({"uid":uid, "forward":"False"})
                res = requests.post(url, data=payload)
                print "Response from courses: " + res.text
                if res.status_code not in ok_put_post_response:
                    undo_event(old_record, sender, uid, "post")
                    return "Unsuccessful change", 409
            else: # course
                print "Courses added a student: " + uid
                # courses added student to class, tell student MS
                print "Class added " + str(uid) + " to student " + str(cid)
                # url = host + "/students/" + uid + "/courses"
                url = get_url(receiver, uid, sender)
                print "POST to:" + url
                payload = json.dumps({"cid":cid, "forward":"False"})
                res = requests.post(url, data=payload)
                print "Reponse from students: " + res.text
                if res.status_code not in ok_put_post_response:
                    undo_event(old_record, sender, cid, "post")
                    return "Unsuccessful change", 409
    elif action == 'PUT':
        old_dictionary = eval(old_record)
        new_dictionary = eval(new_record)
        if sender is 'students':
            old_list = old_dictionary["cid_list"]
            new_list = new_dictionary["cid_list"]
            changes = compare_lists(old_list, new_list)
            for cid in changes['post']:
                # url = host + "/courses/" + cid + "/students"
                url = get_url(receiver, cid, sender)
                print "POST to:" + url
                payload = json.dumps({"uid":uid, "forward":"False"})
                res = requests.post(url, data=payload)
                if res.status_code not in ok_put_post_response:
                    undo_event(old_record, sender, uid, "put")
            for cid in changes['delete']:
                # url = host + "/courses/" + cid + "/students/" + uid
                url = get_url(receiver, cid, sender, uid)
                print "DELETE to:" + url
                payload = json.dumps({"uid":uid, "forward":"False"})
                res = requests.delete(url, data=payload)
                if res.status_code not in ok_delete_from_collection_response:
                    undo_event(old_record, sender, uid, "put")
                    return "Unsuccessful change", 409
        else:
            old_list = old_dictionary["uid_list"]
            new_list = new_dictionary["uid_list"]
            changes = compare_lists(old_list, new_list)
            for uid in changes['post']:
                # url = host + "/students/" + uid + "/courses"
                url = get_url(receiver, uid, sender)
                print "POST to:" + url
                payload = json.dumps({"cid":cid, "forward":"False"})
                res = requests.post(url, data=payload)
                if res.status_code not in ok_put_post_response:
                    undo_event(old_record, sender, cid, "put")
                    return "Unsuccessful change", 409
            for uid in changes['delete']:
                # url = host + "/students/" + uid + "/courses/" + cid
                url = get_url(receiver, uid, sender, cid)
                print "DELETE to:" + url
                payload = json.dumps({"cid":cid, "forward":"False"})
                res = requests.delete(url, data=payload)
                if res.status_code not in ok_delete_from_collection_response:
                    undo_event(old_record, sender, cid, "put")
                    return "Unsuccessful change", 409
    elif action == 'DELETE':
        if sender is 'students': # tell courses we are deleting the student
            # Delete from collection
            if len(cid) > 1:
                # url = host + "/courses/" + cid + "/students/" + uid
                url = get_url(receiver, cid, sender, uid)
                print "DELETE to:" + url
                payload = json.dumps({"uid":uid, "forward":"False"})
                res = requests.delete(url, data=payload)
            else: # remove student from all classes
                old_dictionary = eval(old_record)
                cid_list = old_dictionary["cid_list"]
                for cid in cid_list:
                    # url = host + "/courses/" + str(cid) + "/students/" + uid
                    url = get_url(receiver, cid, sender, uid)
                    print "DELETE to:" + url
                    payload = json.dumps({"uid":uid, "forward":"False"})
                    res = requests.delete(url, data=payload)
        else:
            if len(new_record) > 1:
                # url = host + "/students/" + uid + "/courses/" + cid
                url = get_url(receiver, uid, sender, cid)
                print "DELETE to:" + url
                payload = json.dumps({"cid":cid, "forward":"False"})
                res = requests.delete(url, data=payload)
            else: # the class is gone
                old_dictionary = eval(old_record)
                uid_list = old_dictionary["uid_list"]
                for uid in uid_list:
                    # url = host + "/students/" + str(uid) + "/courses/" + cid
                    url = get_url(receiver, uid, sender, cid)
                    print "DELETE to:" + url
                    payload = json.dumps({"cid":cid, "forward":"False"})
                    res = requests.delete(url, data=payload)
    data = {'received':request.data}
    return response(data, 200)

def undo_event(old_record, sender, sender_id, action):
    print "Error response. Undoing event."
    record = eval(old_record)
    del record['_id']
    # Remove immutable properties
    if sender == 'course':
        del record['cid']
        record['uid_list'] = ",".join(record['uid_list'])
    else:
        del record['uid']
        record['cid_list'] = ",".join(record['cid_list'])
    record["forward"] = "False"
    payload = json.dumps(record)
    url = get_url(sender, sender_id)
    if action == 'DELETE':
        sender_key = 'uid' if sender is 'students' else 'cid'
        post_data = {sender_key:sender_id,"forward":"False"}
        # Create an empty student with uid and update the information
        print "POST to: " + post_url(url) + " data: " + post_data
        res = requests.post(post_url(url), data=post_data)
        print "PUT to: " + url + " data: " + payload
        res = requests.put(url, data=payload)
    else:
        print "PUT to: " + url + " data: " + payload
        res = requests.put(url, data=payload)

# URL variations:
# POST ../students
# PUT, DELETE ../students/uid
# POST ../students/uid/courses
# PUT, DELETE ../students/uid/courses/cid
# POST ../courses
# PUT, DELETE ../courses/cid
# POST ../courses/cid/students
# PUT, DELETE ../courses/cid/students/uid
def get_url(resource, pkey="", collection="", fkey=""):
    print "host is ", host
    url = host + ('/').join([resource, pkey, collection, fkey])
    url = re.sub(r"(/)\1+/*$|/$", "", url)
    return url

# Remove identifier from url
# ../students/nb2406/courses/c6998 -> ../students/nb2406/courses
def post_url(url):
    return re.sub(r"/[^/]*$", "", url)

# Helper method to find out what entities to post/delete
def compare_lists(list1, list2):
    post = filter(lambda i: i not in list1, list2) # new entities
    delete = filter(lambda i: i not in list2, list1) # gone entities
    return {"post":post, "delete":delete}

def is_id(s):
    return re.match(r".*id", s)

def is_idlist(s):
    return re.match(r".*id_list", k)

if __name__ == '__main__':
    main(sys.argv[1:])
