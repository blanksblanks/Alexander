# Tutorials being followed:
# http://blog.luisrei.com/articles/flaskrest.html
# http://api.mongodb.org/python/current/tutorial.html

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

# Import and initialize Mongo DB
import pymongo
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
collection = db.test_collection

#POST
post = {"firstName": "Agustin", "lastName": "Chanfreau", "uid": "ac3680", "email": "ac3680@columbia.edu", 
        "enrolledCourses": ["COMS123", "COMS1234", "COMS12345"], "pastCourses": ["COMS948", "COMS94", "COMS9841"]}#, "date": datetime.datetime.utcnow()}
posts = db.posts
collection.remove({}) # start clear
posts.remove() # start clear
post_id = posts.insert_one(post).inserted_id


post = {"firstName": "Agustasdasdin", "lastName": "Chaasdau", "uid": "ab3680", "email": "ab3680@columbia.edu", 
        "enrolledCourses": ["COMS123", "COMS1234", "COMS12345"], "pastCourses": ["COMS948", "COMS94", "COMS9841"]}#, "date": datetime.datetime.utcnow()}
post_id = posts.insert_one(post).inserted_id


# GET .../students - returns all information for all students
@app.route('/students', methods = ['GET'])
def all_users():
    r = posts.find() # r is a cursor
    l = list(r) # l is a list
    return dumps(l)

# GET .../students/<uid> - returns all information for specified student
@app.route('/students/<uid>', methods = ['GET'])
def api_users(uid):
    record = posts.find_one({"uid": uid})
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record)
    else:
        return not_found()
        
# GET .../students/<uid>/courses - returns enrolledCourses for specified student
@app.route('/students/<uid>/courses', methods = ['GET'])
def get_student_courses(uid):
    print "looking for", uid
    record = posts.find_one({"uid": uid})
    if record:
        print "Found matching record for UID: ", uid
        return dumps(record["enrolledCourses"])
    else:
        return not_found()
    
    
    
    
    
    
    
    
    
        # #This needs to be configurable
    # for each in posts.find_one({"uid": uid}):
        # #print each
        # #print posts.find_one({"uid": uid})[each]
        # if (each == "firstName"):
            # firstName1 = posts.find_one({"uid": uid})[each]
        # if (each == "lastName"):
            # lastName1 = posts.find_one({"uid": uid})[each]
        # if (each == "uid"):
            # uid1 = posts.find_one({"uid": uid})[each]
        # if (each == "email"):
            # email1 = posts.find_one({"uid": uid})[each]
        # if (each == "enrolledCourses"):
            # enrolledCourses1 = posts.find_one({"uid": uid})[each]
        # if (each == "pastCourses"):
            # pastCourses1 = posts.find_one({"uid": uid})[each]
            
    # #print json.dump(posts.find_one({"uid": uid}))
    # return jsonify(firstName=firstName1, lastName=lastName1, uid=uid1, email=email1, enrolledCourses=enrolledCourses1, pastCourses=pastCourses1)
    
    

    
# @app.route('/messages', methods = ['POST'])
# def api_message():

    # if request.headers['Content-Type'] == 'text/plain':
        # return "Text Message: " + request.data

    # elif request.headers['Content-Type'] == 'application/json':
        # return "JSON Message: " + json.dumps(request.json)

    # elif request.headers['Content-Type'] == 'application/octet-stream':
        # f = open('./binary', 'wb')
        # f.write(request.data)
        # f.close()
        # return "Binary message written!"

    # else:
        # return "415 Unsupported Media Type"
    
    
#POST
#post = {"firstName": "Agustin", "lastName": "Chanfreau", "uid": "ac3680", "email": "ac3680@columbia.edu", 
#        "enrolledCourses": ["COMS123", "COMS1234", "COMS12345"], "pastCourses": ["COMS948", "COMS94", "COMS9841"], "date": datetime.datetime.utcnow()}
#posts = db.posts
#post_id = posts.insert_one(post).inserted_id

    #if userid in uid:
    #    return jsonify({userid:uid[userid]})
    #else:
    #    return not_found()    
    
    
    
    
@app.errorhandler(404)
def not_found(error=None):
    message = {
            'status': 404,
            'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp



@app.route('/hello2', methods = ['GET'])
def api_hello2():
    data = {
        'hello'  : 'world',
        'number' : 3
    }
    js = json.dumps(data)

    resp = jsonify(data)
    resp.status_code = 200
    resp.headers['Link'] = 'http://luisrei.com'

    return resp







@app.route('/messages', methods = ['POST'])
def api_message():

    if request.headers['Content-Type'] == 'text/plain':
        return "Text Message: " + request.data

    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"











@app.route('/echo', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
def api_echo():
    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PATCH':
        return "ECHO: PATCH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"








@app.route('/hello')
def api_hello():
    if 'name' in request.args:
        return 'Hello ' + request.args['name']
    else:
        return 'Hello John Doe'

		
		
		
		
		
@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/articles')
def api_articles():
    return 'List of ' + url_for('api_articles')

@app.route('/articles/<articleid>')
def api_article(articleid):
    return 'You are reading ' + articleid

if __name__ == '__main__':
    app.run(debug=True)