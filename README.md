# Alexander

A student and course management system of four microservices:
* students
* courses
* integrator
* router

Useful references:
* http://blog.luisrei.com/articles/flaskrest.html
* http://api.mongodb.org/python/current/tutorial.html
* pymongo functions: http://altons.github.io/python/2013/01/21/gentle-introduction-to-mongodb-using-pymongo/
* using curl for HTTP requests: http://curl.haxx.se/docs/httpscripting.html

Example Tests for Students:
```
$ python integrator.py courses 9001 1 students 9002
$ python students.py
$ curl -X DELETE http://localhost:9002/students/ac3680

# To interact with integrator directly (testing only, users should never talk to integrator)
$ curl -X POST http://127.0.0.1:5000/9002/integrator/Steve_Jobs/DELETE
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

Invocation:
```
mongod --dbpath ~/Desktop/Alexander/api/data/db
python courses.py
python students.py

```

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
