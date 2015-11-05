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
# Get all students
curl -X GET http://localhost:9002/students

# Get one student
curl -X GET http://localhost:9002/students/ac3680

# Post a new student to the database
curl --data "firstName=Melanie&lastName=Hsu&uid=mlh2197" http://127.0.0.1:9002/students

# Delete a student
curl -X DELETE http://localhost:9002/students/ac3680

# Add course to student's list of courses
curl -X PUT http://localhost:9002/students/ab3680/courses/COMS6998

# Delete course from student's list of courses
curl -X DELETE http://localhost:9002/students/ac3680/courses/COMS1234

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
curl -X POST http://127.0.0.1:9001/courses/add/course/COMSW4111

# Add a student to the course:
curl -X PUT http://127.0.0.1:9001/courses/add/student/COMSW4111/mlh2197

# Remove a student from the course:
curl -X DELETE http://127.0.0.1:9001/courses/remove/student/COMSW4111/mlh2197

# Remove a course from the database:
curl -X DELETE http://127.0.0.1:9001/courses/remove/course/COMSW4111
```
