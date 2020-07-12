from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
from keystoneauth1 import exceptions
import datetime
import requests
import json

logged = False
sessionRequest = requests.session()
citiesNames = []
metrics_list = []

def login():
    global logged
    print("Started login")
    auth = v3.Password(auth_url='http://252.3.39.6:5000/v3',
                    user_id='8bb753b2db8a40dd89c3cce466905716',
                    password='openstack',
                    project_id='674523dc283046d5b1812811e24aa90f')
    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    print("Session obtained")
    try:
        token = sess.get_token()
        sessionRequest.headers.update({'X-AUTH-TOKEN': token})
    except exceptions.Unauthorized:
        print("Authentication failed")
        exit()
    logged = True
    print("Authentication succeded")

def retrieve_metrics():
    global metrics_list
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    response = sessionRequest.get('http://252.3.39.61:8041/v1/metric')
    metrics_list = json.loads(response.text)

def getAllMetrics():
    global metrics_list
    if(logged==False):
        print("Authentication failed. Retry login")
        login()
    for metric in metrics_list:
        response = sessionRequest.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?aggregation=min&refresh=true')
        items = json.loads(response.text)
        for item in items:
            print("City name:", metric['name'],"Values:", item[2])

def getAllCities():
    global citiesNames, logged
    if(logged==False):
        print("Authentication failed. Retry login")
        login()
    citiesNames.clear()
    for metric in metrics_list:
        citiesNames.append(metric['name'])

def getCity(cityName):
    global logged
    if(logged==False):
        print("Authentication failed. Retry login")
        login()
    for metric in metrics_list:
        if(metric['name'] == cityName):   
            response = sessionRequest.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?refresh=true')
            items = json.loads(response.text)
            for item in items:
                print("City name:", metric['name'],"Values:", item[2],"Timestamp", item[0])
            return 
    print(cityName,"is not available in Gnocchi DB")
            
def getStatItaly(agg_operation):
    global logged
    if(logged==False):
        print("Authentication failed. Retry login")
        login()
    agg_data = ''
    for metric in metrics_list:
        agg_data = agg_data + '('+metric['id']+' '+agg_operation+')'
    print("minData",agg_data)
    query = '{"operations":"(aggregate '+agg_operation+' (metric '+agg_data+'))"}'
    print("query",query)
    response = sessionRequest.post('http://252.3.39.61:8041/v1/aggregates/',data=query, headers = {'Content-Type': 'application/json'})
    items = json.loads(response.text)
    print("items",items)
    #TODO Mettere le stampe in maniera più decente

def request():
    for metric in metrics_list:
        if metric['name'] == 'metrica1':
            response = sessionRequest.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?refresh=true')
            items = json.loads(response.text)
            print("Items:", items)  

def help():
    print("The available commands are: \n  \
        - !list -> Showing all the cities available\n  \
        - !city <city_name> -> Showing pollution for the selected city\n  \
        - !italy <max/min/mean> -> Showing the information selected for Italy's pollution\n  \
        - !help -> Showing all commands\n  \
        - !quit -> Close the program")
            
if __name__ == "__main__":
    login()
    retrieve_metrics()
    help()
    getAllMetrics()
    while(True):
        print("Which city's pollution would you like to see?")
        choose = input(">")
        command = choose.split(" ")
        if(command[0] == "!list"):
            getAllCities()
            for cityName in citiesNames:
                print("City:",cityName)
        elif(command[0] == "!city"):
            if(len(command) < 2):
                print("Insert also the city name")
                help()
            else:
                getCity(command[1])
        elif(command[0] == "!italy"):
            if(len(command) != 2):
                print("Insert also the type of aggregation")
                help()
            if(command[1] == 'max' or command[1] == 'min' or command[1] == 'mean'):
                getStatItaly(command[1])
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
    #TODO risolvere problema La Spezia
    #TODO nome dei metodi e variabili
    #request()
