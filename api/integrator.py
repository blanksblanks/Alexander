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

@app.route('/integrator', methods = ['GET', 'POST'])
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
