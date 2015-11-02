# The integrator micro-service
# It logs every transaction but will not always inform the other MS about the changes

# Cases where courses will call integrator:
# 	A course has been canceled
#
# Cases where students will call integrator:
#	Student adds a class
#	Student deletes a class
#	Student leaves the university (dropping all classes)
#	Student changes their name (must provide both first and last name)*
#	Student updates past courses*

# *: do not tell other MS about this (the change will not affect them)
# It is essential that each MS, including partitions, has its own distinct IP address

import os
import sys
import datetime
import pprint
import threading
from netaddr import *

from bson.json_util import dumps
import requests

# Import and initialize Flask
from flask import Flask, url_for
from flask import request
from flask import json
from flask import Response
from flask import jsonify
app = Flask(__name__)

# python integrator.py <url for courses> <IP for courses> <number of student partitions> 
# <list of student paritions followed by their IP>
# ex. python integrator.py courses coursesIP 2 students1 students1_IP students2 students2_IP 

courses = None
coursesIP = None
students = {} # dictionary of studentsURL: studentsIP
acceptedOps = ['POST', 'GET', 'PUT', 'DELETE']

def main(argv):
	if (len(argv) < 5):
		print "Too few command-line arguments."
		sys.exit(1)

	ips = []
	expectedUniqueIPs = 0

	global courses
	courses = argv[0]

	global coursesIP
	coursesIP = argv[1]
	ips.append(coursesIP)
	expectedUniqueIPs += 1

	numberOfPartitions = int(argv[2])
	argNumber = 3

	global students
	for i in range(numberOfPartitions):
		students[argv[argNumber]] = argv[argNumber+1]
		ips.append(argv[argNumber+1])
		argNumber += 2
		expectedUniqueIPs += 1

	# ensure that the IP addresses are all distinct!
	if (len(set(ips)) < expectedUniqueIPs):
		print "Each IP address must be distinct (including partitions)."
		sys.exit(1)

	app.run()

# Check that the requester's IP address belongs to courses or one of the students micro-services
def checkIP(ip_address):
	if (IPAddress(ip_address) == IPAddress(coursesIP)):
		return True
	for k, v in students.iteritems():
		if IPAddress(ip_address) == IPAddress(v):
			return True
	return False	

# Check that the requester's action is one of the CRUD operations
def checkAction(action):
	if (action in acceptedOps):
		return True
	else:
		return False

# Creates response to return to the user
def response(data, code):
	js = json.dumps(data)
	resp = Response(js, status = code, mimetype='application/json')
	return resp

# Log message format: <timestamp> <requester IP> [<pkeys>] [<fkeys>] [<original non-primary key>] [<changed non-primary key>] <CRUD operation>
# Leave any given array as empty parentheses if there aren't any
# Ex.1 Steve Jobs leaves UNI: 
#	2015-11-01T16:19:03.336866 127.0.0.1 [Steve Jobs] [] [] [] DELETE
# Ex.2 COMS4111-3 is cancelled
#	2015-11-01T16:19:43.202877 127.0.0.1 [COMS4111-3] [] [] [] DELETE
# Ex.3 Melanie Hsu changed her name to Princess Sally
#	2015-11-01T16:06:20.702367 127.0.0.1 [mlh2197] [] [Melanie Hsu] [Princess Sally] PUT
# Ex.4 Student with uni=mlh2197 dropped biology lab (BIOLS2501)
#	2015-11-01T16:09:40.726156 127.0.0.1 [mlh2197] [] [BIOLS2501] [None] DELETE
# Ex.5 Student with UNI=wvb2103 added COMS4111-1
#	2015-11-01T16:45:59.339502 127.0.0.1 [wvb2103] [COMS4111-1] [] [] POST
# Ex.6 Student with UNI=wvb2103 dropped COMS4111-2
#	2015-11-01T16:46:23.380283 127.0.0.1 [wvb2103] [COMS4111-2] [] [] DELETE
def writeToLog(message):
	with open("log.txt", "a") as myfile:
		myfile.write(message + "\n")

def deleteFromLog(timestamp):
	# Read all the lines
	f = open("log.txt", "r")
	lines = f.readlines()
	f.close()

	# Look for the line to delete
	lineNumber = 1
	for l in lines:
		if timestamp in l:
			break
		lineNumber += 1

	# Write all lines except for the one to delete into a new file
	lineCount = 1
	message = ""
	n = open("newlog.txt", "a")
	for line in lines:
		if lineCount != lineNumber:
			n.write(line)
		else:
			message += line
		lineCount += 1
	n.close()
	if (len(message) > 0):
		os.rename("newlog.txt", "log.txt")
	return message

# Method to help split the key and prepare it in the correct format for the log
def formatKey(key):
	substring = " ["
	key = key.replace("_", " ")
	for i in range(len(key)):
		substring += key[i]
	substring += "]"
	return substring

# Call the other micro-services
def notifyMS(requesterIP, message):
	sender = None
	# determine if students or courses was the sender
	if (IPAddress(requesterIP) == IPAddress(coursesIP)):
		sender = 'course'
	else:
		for k, v in students.iteritems():
			if IPAddress(requesterIP) == IPAddress(v):
				sender = 'student'

	# determine who to send request to based on the sender
	if (sender == 'course'): # broadcast to students
		for k, v in students.iteritems():
			print "CONTACTED STUDENTS"
			r = requests.post(IPAddress(v), data = message)
	else:
		print "CONTACTED COURSES"
		r = requests.post(IPAddress(coursesIP), data = message)

# POST with primary key only (primary keys are cid or uid)
# The integrator will inform the other MS about these changes
# To call: curl -X POST http://127.0.0.1:9001/integrator/<primary_key_value_separated_by_underlines>/<CRUD op>
# Ex1: curl -X POST http://127.0.0.1:9001/integrator/Steve_Jobs/DELETE where Steve Jobs leaves uni
# Ex2: curl -X POST http://127.0.0.1:9001/integrator/COMS4111-3/DELETE where COMS4111-3 is cancelled
@app.route('/integrator/<primary_key>/<action>', methods = ['POST'])
def post_key_POST_OR_DEL(primary_key, action):
	ip = request.remote_addr #save requester's IP address
	if (checkIP(ip)):
		if (not checkAction(action)):
			data = {'error':'Specified protocol not a CRUD operation'}
			return response(data, 403)
	else:
		data = {'error':'Unknown requester IP address'}
		return response(data, 403)
	
	# Construct the message to log
	message = str(datetime.datetime.now().isoformat()) + " " + str(ip)
	message += formatKey(primary_key) + " [] [] []"
	message += " " + str(action)

	# Log the message
	writeToLog(message)

	# These actions meaningless to other MS, plus the Courses & Students DB disallow modifications to primary keys
	#if (action != 'PUT' and action != 'GET'): 
		# inform the other MS(s) of this change by sending message to it
		# The other MS will call /integrator/<timestamp>
		#notifyMS(ip, message) 
	
	# TODO: problem, what if the recipient MS never calls /integrator/<timestamp>?

	# Return the logged message to the requester
	data = {'logged':message}
	return response(data, 200)

# The integrator will NOT inform the other MS about these changes
# POST with non-primary key, requester can specify any of the four operations
# To call: curl -X POST http://127.0.0.1:9001/integrator/<old_keys_vals_separated_by_underlines>/<new_key_vals_separated_by_underlines>/<CRUD op>
# Ex.1 curl -X POST http://127.0.0.1:9001/integrator/mlh2197/Melanie_Hsu/Princess_Sally/PUT
# where Melanie Hsu (UNI: mlh2197) changed her name to Princess Sally
# Ex.2 curl -X POST http://127.0.0.1:9001/integrator/mlh2197/BIOLS2501/None/DELETE
# where student with UNI mlh2197 dropped Biology Lab
@app.route('/integrator/<primary_key>/<key_oldval>/<key_newval>/<action>', methods = ['POST'])
def post_key_PUT(primary_key, key_oldval, key_newval, action):
	ip = request.remote_addr #save requester's IP address
	if (checkIP(ip)):
		if (not checkAction(action)): #make sure requester specified a CRUD operation
			data = {'error':'Specified protocol not a CRUD operation'}
			return response(data, 403)
	else:
		data = {'error':'Unknown requester IP address'}
		return response(data, 403)
	
	# Construct the message to log
	message = str(datetime.datetime.now().isoformat()) + " " + str(ip)
	message += formatKey(primary_key)
	message += " []"
	message += formatKey(key_oldval)
	message += formatKey(key_newval)
	message += " " + str(action)

	# Log the message
	writeToLog(message)

	# Return the logged message to the requester
	data = {'logged':message}
	return response(data, 200)

# POST with primary & foreign key
# Ex.1 curl -X POST http://127.0.0.1:9001/integrator/wvb2103/COMS4111-1/POST
# where student with UNI=wvb2103 added COMS4111-1
# Ex.2 curl -X POST http://127.0.0.1:9001/integrator/wvb2103/COMS4111-2/DELETE
# where student with UNI=wvb2103 dropped COMS4111-2
@app.route('/integrator/<pkey>/<fkey>/<action>', methods = ['POST'])
def post_2key(pkey, fkey, action):
	ip = request.remote_addr #save requester's IP address
	if (checkIP(ip)):
		if (not checkAction(action)): #make sure requester specified a CRUD operation
			data = {'error':'Specified protocol not a CRUD operation'}
			return response(data, 403)
	else:
		data = {'error':'Unknown requester IP address'}
		return response(data, 403)

	# Construct the message to log
	message = str(datetime.datetime.now().isoformat()) + " " + str(ip)
	message += formatKey(pkey)
	message += formatKey(fkey)
	message += " []"
	message += " []"
	message += " " + str(action)

	# Log the message
	writeToLog(message)

	# These actions meaningless to other MS, plus the Courses & Students DB disallow modifications to primary keys
	#if (action != 'PUT' and action != 'GET'): 
	#	notifyMS(ip, message)

	# Return the logged message to the requester
	data = {'logged':message}
	return response(data, 200)

# POST message from MS telling integrator to delete a log message with a certain timestamp
# TODO: problem, what do we do with the non-essential logs? the ones that don't affect the other DB
# Ex. curl -X POST http://127.0.0.1:9001/integrator/2015-11-01T16:53:51.515837
# which means delete the log message that has this timestamp
@app.route('/integrator/<timestamp>', methods = ['POST'])
def delete_logEntry(timestamp):
	ip = request.remote_addr #save requester's IP address
	message = deleteFromLog(timestamp)
	if (len(message) > 0):
		data = {'deleted':message}
		return response(data, 200)
	else:
		data = {'error':'Message does not exist'}
		return response(data, 404)

if __name__ == '__main__':
	main(sys.argv[1:])