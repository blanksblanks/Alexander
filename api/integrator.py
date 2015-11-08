# The integrator micro-service
# It logs every transaction but will not always inform the other MS about the changes

# *: do not tell other MS about this (the change will not affect them)
# It is essential that each MS, including partitions, has its own distinct port

import os
import sys
import datetime
import pprint
import thread

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
#		list the following:) <studentMS_URL> <studentMS_port>
#ex. python integrator.py http://localhost:9001 9001 1 http://localhost:9002 9002

courses = None
courses_port = None
courses_list = []
students_list = []
students = {} # dictionary of studentsURL: studentsPort

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
def post_key_POST_OR_DEL(primary_key):
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
				sender = 'course'
			else:
				for k, v in students.iteritems():
					if port == int(v):
						sender = 'student'
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
			if sender == 'student':
				global students_list
				students_list.append(uid)
				print "student added: " + uid
				print "updated students list: " + str(students_list)
			else:
				global courses_list # add to the list of existing courses
				courses_list.append(cid)
				print "course added: " + cid
				print "updated courses list: " + str(courses_list)
		else: # record update
			print "record update"
			if sender == 'student':
				# student added a class, tell courses MS
				if (cid in courses_list):
					print "Students added " + str(uid) + " to class " + str(cid)
					url = "http://127.0.0.1:" + str(courses_port) + "/courses/" + cid + "/students"
					payload = json.dumps({"uid":uid, "forward":"False"})
					res = requests.post(url, data=payload)
					#print "Notified courses that " + str(uid) + " added class " + str(cid)
					print "Response from courses: " + res.text
			else:
				print "Courses added a student: " + uid
				# courses added student to class, tell student MS
				for k, v in students.iteritems():
					url = "http://127.0.0.1:" + str(int(v)) + "/students/" + uid + "/courses"
					print url
					payload = json.dumps({"cid":cid, "forward":"False"})
					res = requests.post(url, data=payload)
					print "Reponse from students: " + res.text
	elif action == 'PUT':
		print 'PUT'
	elif action == 'DELETE':
		if sender == 'student': # tell courses we are deleting the student
			if len(cid) > 1:
				url = "http://127.0.0.1:" + str(courses_port) + "/courses/" + cid + "/students/" + uid
				payload = json.dumps({"uid":uid, "forward":"False"})
				res = requests.delete(url, data=payload)
			else: # remove student from all classes
				old_dictionary = eval(old_record)
				cid_list = old_dictionary["cid_list"]
				for v in cid_list:
					url = "http://127.0.0.1:" + str(courses_port) + "/courses/" + str(v) + "/students/" + uid
					payload = json.dumps({"uid":uid, "forward":"False"})
					res = requests.delete(url, data=payload)
		else:
			if len(new_record) > 1:
				for k, v in students.iteritems():
					url = "http://127.0.0.1:" + str(int(v)) + "/students/" + uid + "/courses/" + cid
					payload = json.dumps({"cid":cid, "forward":"False"})
					res = requests.delete(url, data=payload)
			else: # the class is gone
				for k, v in students.iteritems():
					old_dictionary = eval(old_record)
					uid_list = old_dictionary["uid_list"]
					for w in uid_list:
						url = "http://127.0.0.1:" + str(int(v)) + "/students/" + str(w) + "/courses/" + cid
						payload = json.dumps({"cid":cid, "forward":"False"})
						res = requests.delete(url, data=payload)
	data = {'received':request.data}
	return response(data, 200)

if __name__ == '__main__':
	main(sys.argv[1:])