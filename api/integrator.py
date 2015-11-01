import sys
import datetime
import pprint
from netaddr import *

from bson.json_util import dumps

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

	global courses
	courses = argv[0]

	global coursesIP
	coursesIP = argv[1]

	numberOfPartitions = int(argv[2])
	argNumber = 3

	global students
	for i in range(numberOfPartitions):
		students[argv[argNumber]] = argv[argNumber+1]
		argNumber += 2

	app.run( # curl -X POST/GET http://0.0.0.0:9000/integrator from another terminal window to send requests
		host = "127.0.0.1",
		port = int("9001")
	)

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

# Log message format: <timestamp> <requester IP> [<pkeys>] [<fkeys> IF EXISTS] <CRUD operation>
# Ex. Steve Jobs leaves UNI: 
#	2015-11-01T15:26:22.729117 127.0.0.1 [Steve Jobs] DELETE
# Ex. COMS4111-3 is cancelled
#	2015-11-01T15:27:21.546925 127.0.0.1 [COMS4111-3] DELETE
def writeToLog(message):
	print "Written to log"

# Cases where courses will call integrator:
# 	A course has been canceled
#
# Cases where students will call integrator:
#	Student adds a class
#	Student deletes a class
#	Student leaves the university (dropping all classes)
#	Student changes their name (must provide both first and last name)
#	Student updates current coureses
#	Student updates past courses

# POST with key only (primary keys are cid or uid), supports requester POST & DELETE only!
# To call: curl -X POST http://127.0.0.1:9001/integrator/<pkeys_separated_by_underlines>/<CRUD op>
# Ex: curl -X POST http://127.0.0.1:9001/integrator/Steve_Jobs/DELETE where Steve Jobs leaves uni
#	  curl -X POST http://127.0.0.1:9001/integrator/COMS4111-3/DELETE where COMS4111-3 is cancelled
@app.route('/integrator/<key>/<action>', methods = ['POST'])
def post_pkey(key, action):
	ip = request.remote_addr #save requester's IP address
	if (checkIP(ip)):
		if (not checkAction(action)): #make sure requester specified a CRUD operation
			data = {'error':'Specified protocol not a CRUD operation'}
			return response(data, 403)
	else:
		data = {'error':'Unknown requester IP address'}
		return response(data, 403)
	# Construct the message to log
	message = str(datetime.datetime.now().isoformat()) + " " + str(ip) + " ["
	split_key = key.replace("_", " ")
	for i in range(len(split_key)):
		message += split_key[i]
	message += "] " + str(action)

	# Log the message
	writeToLog(message)

	# Return the logged message to the requester
	data = {'logged':message}
	return response(data, 200)

# POST with key only, supports requester PUT
@app.route('/integrator/<key_oldval>/<key_newval>/<action>', methods = ['POST'])


# POST with primary & foreign key
@app.route('/integrator/<pkey>/<fkey>/<action>', methods = ['POST'])
def post_2key(pkey, fkey, action):
	print pkey
	print fkey 
	print action
	return "Hello World!"


# Action being taken
# What operation it is
# Each micro service needs a different IP

# integrator do post operations?*

# Do NOT delete this! We will need parts of this later
@app.route('/integrator/', methods = ['GET', 'POST'])
def integrator():
	if request.method == 'POST':
		ip = request.remote_addr #save requester's IP address
		if (checkIP(ip)):
			return "POST request from " + str(ip) + "\n"
		else:
			return "Unknown requester IP address."
	elif request.method == 'GET':
		ip = request.remote_addr
		if (checkIP(ip)):
			return "GET request from " + str(ip) + "\n"
		else:
			return "Unknown requester IP address.\n"

if __name__ == '__main__':
	main(sys.argv[1:])

#python integrator.py courses course123 2 students students111 students2 students222
