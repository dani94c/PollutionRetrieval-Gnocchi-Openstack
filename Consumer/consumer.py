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

#Retrieve the available metrics
def retrieve_metrics():
    global metrics_list
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    response = session_request.get('http://252.3.39.61:8041/v1/metric')
    if(response.status_code == 200):
        metrics_list = json.loads(response.text)
    else:
        print("ERROR: ", response.status_code,response.reason)
        exit()

'''
def getAllMetrics():
    global metrics_list
    if(logged==False):
        print("Authentication failed. Retry login")
        login()
    for metric in metrics_list:
        response = session_request.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?refresh=true')
        items = json.loads(response.text)
        for item in items:
            print("City name:", metric['name'],"Values:", item[2])
'''

#Print all the cities (metrics) inserted in the Gnocchi DB
def get_all_cities():
    global cities_names, logged
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    cities_names.clear()
    for metric in metrics_list:
        cities_names.append(metric['name'])

#get the min/max/mean among all the values of different cities per hour
def get_stat_italy(agg_operation):
    global logged
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
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
        for item in items["measures"]["aggregated"]:
            print("Time",datetime.datetime.strptime(item[0],"%Y-%m-%dT%H:%M:%S+00:00"),"Pollution",agg_operation,"level:",item[2])    
    else:
        print("ERROR: ", response.status_code,response.reason)
        if(response.status_code == 401):
            #the token has exiperd
            print("Try Again")
            logged = False

#aggregate the specified metric according to the specified stat. Print all the metric's values with timestamp and the corresponding value
def get_all_stat_city(name_city, stat):
    global metrics_list, logged
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    for metric in metrics_list:
        if(metric['name'] == name_city):
            response = session_request.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?aggregation='+stat+'&refresh=true')
            if(response.status_code == 200):
                items = json.loads(response.text)
                for item in items:  
                    print("Time:",item[0],"Pollution",stat,"level:",item[2])
                return
            else:
                print("ERROR: ", response.status_code,response.reason)
                if(response.status_code == 401):
                    #the token has exiperd
                    print("Try Again")
                    logged = False

#aggregate the specified metric according to the specified stat. Print the global minimum/maximum/mean among the minimum/maximum/mean values
def get_stat_city(name_city, stat):
    global metrics_list, logged
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    for metric in metrics_list:
        if(metric['name'] == name_city):
            response = session_request.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?aggregation='+stat+'&refresh=true')
            if(response.status_code == 200):
                items = json.loads(response.text)
                #take the min/max/avg among the elements in the list
                values = np.array([item[2] for item in items])
                if(stat == "min"):
                    print("The min value is:",np.min(values))
                elif(stat == "max"):
                    print("The max value is:",np.max(values))
                elif(stat == "mean"):
                    print("The mean value is:",np.mean(values))
                return
            else:
                print("ERROR: ", response.status_code,response.reason)
                if(response.status_code == 401):
                    #the token has exiperd
                    print("Try Again")
                    logged = False

def help():
    print("The available commands are: \n  \
        - !list -> Showing all the cities available\n  \
        - !city_timeline <city_name> <max/min/mean> -> Showing all the max/min/mean value registered at different time for the selected city\n  \
        - !city_stat <city_name> <max/min/mean> -> Showing the max/min/mean among all the values for the city\n  \
        - !italy <max/min/mean> -> Showing the statistic selected for Italy's pollution\n  \
        - !help -> Showing all commands\n  \
        - !quit -> Close the program")
            
if __name__ == "__main__":
    login()
    retrieve_metrics()
    help()
    #getAllMetrics()
    while(True):
        print("Which city's pollution would you like to see?")
        choose = input(">")
        command = choose.split(" ")
        if(command[0] == "!list"):
            get_all_cities()
            for city_name in cities_names:
                print("City:",city_name)
        elif(command[0] == "!city_timeline"):
            if(len(command) == 3):
                if(command[2] == 'max' or command[2] == 'min' or command[2] == 'mean'):
                    get_all_stat_city(command[1],command[2])
                else:
                    print("Wrong command, retry")
                    help()
            else:
                print("Wrong command, retry")
                help()
        elif(command[0] == "!city_stat"):
            if(len(command) == 3):
                if(command[2] == 'max' or command[2] == 'min' or command[2] == 'mean'):
                    get_stat_city(command[1],command[2])
                else:
                    print("Wrong command, retry")
                    help()
            else:
                print("Wrong command, retry")
                help()
        elif(command[0] == "!italy"):
            if(len(command) != 2):
                print("Insert also the type of aggregation")
                help()
            elif(command[1] == 'max' or command[1] == 'min' or command[1] == 'mean'):
                get_stat_italy(command[1])
            else:
                print("Wrong type of aggregation")
                help()
        elif(command[0] == "!help"):
            help()
        elif(command[0] == "!quit"):
            exit()
        else:
            print("Command not found")
            help()