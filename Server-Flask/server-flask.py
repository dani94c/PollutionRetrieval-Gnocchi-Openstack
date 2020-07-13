#!flask/bin/python

from flask import Flask, jsonify

app = Flask(__name__)

from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1 import exceptions
import numpy as np
import datetime
import requests
import json

logged = False
session_request = requests.session()
cities_names = []
metrics_list = []

# Login function - Obtain the token with Keystone
def login():
    global logged
    print("Started login")
    auth = v3.Password(auth_url='http://252.3.39.6:5000/v3',
                    user_id='8bb753b2db8a40dd89c3cce466905716',
                    password='openstack',
                    project_id='674523dc283046d5b1812811e24aa90f')
    #create a session with the previous credentials (taken from horizon UI)
    sess = session.Session(auth=auth)
    #Instantiate a Client using a Session to provide the authentication plugin, SSL/TLS certificates
    keystone = client.Client(session=sess)
    print("Session obtained")
    try:
        #get the token for the session
        token = sess.get_token()
        #the token is in the header of every requests to the Gnocchi DB
        session_request.headers.update({'X-AUTH-TOKEN': token})
    except exceptions.Unauthorized:
        print("Authentication failed")
        exit()
    logged = True
    print("Authentication succeded")

#Utility function used to obtain the list of all the metrics in GnocchiDB
def retrieve_metrics():
    global metrics_list
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    response = session_request.get('http://252.3.39.61:8041/v1/metric')
    if(response.status_code == 200):
        metrics_list = json.loads(response.text)
    return response.status_code



# -------- Get-Post functions implementation --------

#Print all the cities (metrics) inserted in the Gnocchi DB
@app.route('/v1/cities', methods=['GET'])
def get_all_cities():
    global metrics_list, cities_names
    status_code = retrieve_metrics()
    if(status_code == 200):
        cities_names.clear()
        for metric in metrics_list:
            cities_names.append(metric['name'])
        return jsonify(cities_names)
    else:
        return jsonify("ERROR"), status_code

#Get the min/max/mean value among all the values of different cities per hour, for the pollution level in Italy
@app.route('/v1/italy/<agg_operation>', methods=['GET'])   
def get_stat_italy(agg_operation):
    status_code = retrieve_metrics()
    if(status_code == 200):
        agg_data = ''
        for metric in metrics_list:
            agg_data = agg_data + '('+metric['id']+' '+agg_operation+')'
        #the query has a format like {{"operations":"(aggregate 'min' (metric ( metric__id_1 min) ( metric_id_2 min) ( metric_id_3 min)))"}}
        #for each metric aggregates using the specified statistic then for each hour aggregate the values among all the metrics for the specified statistic
        query = '{"operations":"(aggregate '+agg_operation+' (metric '+agg_data+'))"}'
        response = session_request.post('http://252.3.39.61:8041/v1/aggregates/',data=query, headers = {'Content-Type': 'application/json'})
        if(response.status_code == 200):
            items = json.loads(response.text)
            #response has the format {"measures": {"aggregated":[ [item1],[item2], ..... ]}}
            result = []
            for item in items["measures"]["aggregated"]:
                data = { "Time" : datetime.datetime.strptime(item[0],"%Y-%m-%dT%H:%M:%S+00:00"),'"Pollution ' + agg_operation + ' level"' : item[2]}   
                result.append(data)
            return jsonify(result)
        else:
            return jsonify(response.reason), response.status_code
    else:
        return jsonify("ERROR"), status_code

#Get a timeline for the specified statistics for the pollution level in the given city
#Aggregate the specified metric according to the specified stat. Print all the metric's values with timestamp and the corresponding value
@app.route('/v1/timeline/<name_city>/<stat>', methods=['GET'])
def get_all_stat_city(name_city, stat):
    global metrics_list
    if(stat == 'min' or stat == 'max' or stat == 'mean'):
        status_code = retrieve_metrics()
        if(status_code == 200):
            for metric in metrics_list:
                if(metric['name'] == name_city):
                    response = session_request.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?aggregation='+stat+'&refresh=true')
                    if(response.status_code == 200):
                        items = json.loads(response.text)
                        result = []
                        for item in items:  
                            data = {"Time" : item[0], '"Pollution ' + stat + ' level"' : item[2]}
                            result.append(data)
                        return jsonify(result)
                    else:
                        return jsonify(response.reason), response.status_code
        else:
            return jsonify("ERROR"), status_code
    return jsonify("ERROR: INCORRECT URL"), 400

#Aggregate the specified metric according to the specified stat. Print the global minimum/maximum/mean among the minimum/maximum/mean values
@app.route('/v1/<name_city>/<stat>', methods=['GET'])
def get_stat_city(name_city, stat):
    global metrics_list
    if(stat == 'min' or stat == 'max' or stat == 'mean'):
        status_code = retrieve_metrics()
        if(status_code == 200):
            for metric in metrics_list:
                if(metric['name'] == name_city):
                    response = session_request.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?aggregation='+stat+'&refresh=true')
                    if(response.status_code == 200):
                        items = json.loads(response.text)
                        #take the min/max/avg among the elements in the list
                        values = np.array([item[2] for item in items])
                        if(stat == "min"):
                            return jsonify({"Pollution min level" : np.min(values)})
                        elif(stat == "max"):
                            return jsonify({"Pollution max level" : np.max(values)})
                        elif(stat == "mean"):
                            return jsonify({"Pollution mean level" : np.mean(values)})
                    else:
                        return jsonify(response.reason), response.status_code
        else:
            return jsonify("ERROR", status_code)
    return jsonify("ERROR: INCORRECT URL"), 400
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
