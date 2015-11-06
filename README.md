# Alexander

##### A student and course management system of four microservices:
* students
* courses
* integrator
* router

Useful References:
* http://blog.luisrei.com/articles/flaskrest.html
* http://api.mongodb.org/python/current/tutorial.html
* pymongo functions: http://altons.github.io/python/2013/01/21/gentle-introduction-to-mongodb-using-pymongo/
* using curl for HTTP requests: http://curl.haxx.se/docs/httpscripting.html

Start Program:
* In separate tabs on the command line:
```
mongod --dbpath ~/Desktop/Alexander/api/data/db
python api/courses.py
python api/students.py
python api/integrator.py courses 9001 1 students 9002
```

Example Tests for Students:
```
Add a student to the database:
curl --data "first_name=Melanie&last_name=Hsu&uid=mlh2197&cid_list=COMS4111,COMS6998&past_cid_list=COMS4118" http://127.0.0.1:9002/students

Get all info on all students:
curl -X GET http://127.0.0.1:9002/students

Get info about one student from the database:
curl -X GET http://127.0.0.1:9002/students/mlh2197

Add a class to a student's schedule:
curl -X POST --data "cid=COMS4156" http://127.0.0.1:9002/students/mlh2197/courses

Delete a class from a student's schedule:
curl -X DELETE http://127.0.0.1:9002/students/mlh2197/courses/COMS4156

Get a student's courses from the database: TRY IT AGAIN
curl -X GET http://127.0.0.1:9002/students/mlh2197/courses

Delete a student:
curl -X DELETE http://127.0.0.1:9002/students/ac3680

Update a student (non-primary key):
curl -X PUT -d first_name=Princess -d last_name=Sally http://127.0.0.1:9002/students/mlh2197
curl -X PUT --data "first_name=Princess&last_name=Sally&cid_list=COMS4111,COMS6998,COMS4115" http://127.0.0.1:9002/students/mlh2197

# As an example of how to interact with integrator directly (testing only, users should never talk to integrator)
curl -X POST http://127.0.0.1:5000/9002/integrator/Steve_Jobs/DELETE
# Response should look like {"logged": "2015-11-02T16:59:16.358478 127.0.0.1 [Steve Jobs] [] [] [] DELETE"}
```
* See above [reference above](http://curl.haxx.se/docs/httpscripting.html) for how to use curl for HTTP requests
* Or if you prefer GUIs, use [Postman](https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop)
* Note that localhost is equivalent to 127.0.0.1
* Note which ports are running the separate microservices:

| Microservice | Port Number|
| ------------- | ------------- |
| Router  | 1234 |
| Integrator | 5000  |
| Courses | 9001 |
| Students | 9002 |

* Additional students microservice partitions run on 9003, 9004, etc.

Example Tests for Courses:
```
# Add a course to the database:
curl -d "cid=COMS6998" http://127.0.0.1:9001/courses

# Get all courses
curl -X GET http://localhost:9001/courses

# Get one course
curl -X GET http://localhost:9001/courses/COMS6998

# Get one course's students
curl -X GET http://localhost:9001/courses/COMS6998/students

# Remove a course from the database:
curl -X DELETE http://127.0.0.1:9001/courses/COMS6998

# Add a student to the course:
curl -X PUT http://127.0.0.1:9001/courses/COMS6998/students/nb2406

# Remove a student from the course:
curl -X DELETE http://127.0.0.1:9001/courses/COMS6998/students/nb2406
```
