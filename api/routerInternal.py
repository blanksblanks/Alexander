# -*- coding: utf-8 -*-
    
from flask import Flask
from flask import Response
from flask import stream_with_context
from flask import request

from werkzeug.routing import BaseConverter

import requests
import json
import pickle
import pdb

app = Flask(__name__)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
                
app.url_map.converters['regex'] = RegexConverter

#Returns a list of ports determined by the first letter of the param
#(Or a list with only a "0" if the uid's first character is not a letter)
#This is used by all re-routes for Students except POST
def getPort(param):
    with open('config', 'rb') as handle:
        routingTable = pickle.loads(handle.read())
    UIDisThere = False
    portList = []
    if param == "":
        for key, value in routingTable.items():
            if value in portList:
                a=1
            else:
                portList.append(value)
        return portList
    for key, value in routingTable.items():
        try:
            if key == param[1]:
                portList.append(value)
                UIDisThere = True
                break
        except:
            portList = []
            portList.append(0)
            return portList
    if UIDisThere == False:
        portList.append(0)
        return portList
    return portList
    
#Returns the target port as single variable - not as list
#This is only used by the student's POST
def postPort(param):
    with open('config', 'rb') as handle:
        routingTable = pickle.loads(handle.read())
    UIDisThere = False
    for key, value in routingTable.items():
        if key == param[0]:
            SinglePort = value
            UIDisThere = True
            break
    if UIDisThere == False:
        SinglePort = 0
        return SinglePort
    return SinglePort

#Any URIs coming in with "/courses..." are re-routed in this function
@app.route("/courses<regex('.*'):param>", methods = ['GET', 'POST', 'PUT', 'DELETE'])
def coursesRoute(param):
    data = {}
    
    #If the data is in string format, convert to json
    if type(request.data) == str:
        jsonData = json.loads(request.data)
    else:
        jsonData = request.form
    
    #A GET request is incoming
    if request.method == 'GET':
            req = requests.get("http://127.0.0.1:9001/courses" + param, stream = True)
            return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
            
    #A POST request is incoming
    elif request.method == 'POST':
        for k,v in jsonData.iteritems():
            data.update({k:v})
        req = requests.post("http://127.0.0.1:9001/courses" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
        
    #A PUT request is incoming
    elif request.method == 'PUT':
        for k,v in jsonData.iteritems():
            data.update({k:v})
        req = requests.put("http://127.0.0.1:9001/courses" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
        
    #A DELETE request is incoming
    elif request.method == 'DELETE':
        for k,v in jsonData.iteritems():
            data.update({k:v})
        req = requests.delete("http://127.0.0.1:9001/courses" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

        
#Any URIs coming in with "/students..." are re-routed in this function
@app.route("/students<regex('.*'):param>", methods = ['GET', 'POST', 'PUT', 'DELETE'])
def studentsRoute(param):

    #If the data is in string format, convert to json
    if type(request.data) == str:
        jsonData = json.loads(request.data)
    else:
        jsonData = request.form

    #Get the list of ports relevant to the incoming
    portList = getPort(param)
    if portList[0] == 0: # UID starts with a letter (invalid)
        return "Invalid UID", 400
        
    data = {}
    
    #GET coming in
    if request.method == 'GET':
    
        #If there is just one Students MS
        if len(portList) == 1:
            req = requests.get("http://127.0.0.1:" + str(portList[0]) + "/students" + param, stream = True)
            return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
            
        #If there are three Students MSs, the get must concatenate three responses
        if len(portList) == 3:
            req1 = requests.get("http://127.0.0.1:" + str(portList[0]) + "/students" + param, stream = True)
            req2 = requests.get("http://127.0.0.1:" + str(portList[1]) + "/students" + param, stream = True)
            req3 = requests.get("http://127.0.0.1:" + str(portList[2]) + "/students" + param, stream = True)
            
            #Concatenate three responses together, separated by ", "
            responseText = req1.text[:-1]
            if len(req2.text) != 2:
                responseText += ", "
            responseText += req2.text[1:-1]
            if len(req3.text) != 2:
                responseText += ", "
            responseText += req3.text[1:]
            return responseText
            
    #POST coming in
    elif request.method == 'POST':
    
        #Populate the data dictionary with the key value pairs coming in from the body
        for k,v in jsonData.iteritems():
            data.update({k:v})
            
        #Get the single target port by finding what letter the UID starts with
        try:
            singlePort = postPort(request.form['uid'])
        except:
            singlePort = postPort(param[1:])

        if singlePort == 0: # The UID did not start with a letter
            return "Invalid UID", 400
        req = requests.post("http://127.0.0.1:" + str(singlePort) + "/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
        
    #PUT coming in
    elif request.method == 'PUT':
        for k,v in jsonData.iteritems():
            data.update({k:v})
        req = requests.put("http://127.0.0.1:" + str(portList[0]) + "/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])
        
    #DELETE coming in
    elif request.method == 'DELETE':
        for k,v in jsonData.iteritems():
            data.update({k:v})
        req = requests.delete("http://127.0.0.1:" + str(portList[0]) + "/students" + param, data=data)
        return Response(stream_with_context(req.iter_content()), content_type = req.headers['content-type'])

if __name__ == '__main__':
    app.run(
        debug = True,
        port = 1235
    )