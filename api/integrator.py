import sys
import datetime
import pprint

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
students = {}

def main(argv):
	if (len(argv) < 5):
		print "Too few command-line arguments."
		sys.exit(1)
	courses = argv[0]
	coursesIP = argv[1]
	numberOfPartitions = int(argv[2])
	argNumber = 3
	for i in range(numberOfPartitions):
		students[argv[argNumber]] = argv[argNumber+1]
		argNumber += 2

	app.run(
		host = "localhost",
		port = int("9000")
	)

@app.route('/integrator', methods = ['GET', 'POST'])
def integrator():
	if request.method == 'POST':
		print "POST"
	else:
		print "GET"

if __name__ == '__main__':
	main(sys.argv[1:])

#python integrator.py courses course123 2 students students111 students2 students222
