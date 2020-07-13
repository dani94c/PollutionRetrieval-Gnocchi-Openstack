from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneauth1 import exceptions
from keystoneclient.v3 import client
from time import sleep
import requests
import datetime
import json
import random

logged = False
session_request = requests.session()
cities_id = []
cities_name = []
                    
# Login function - Obtain the token with Keystone
def login():
    global cities_id, logged
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
    # Retrieving the metric-id
    response = session_request.get('http://252.3.39.61:8041/v1/metric')
    print("Response nel login:", response)
    cities_id.clear()
    metrics_list = json.loads(response.text)
    for metric in metrics_list:
        cities_id.append(metric['id'])
        cities_name.append(metric['name'])

# Post function in order to insert a new value for the metric
def post():
    global cities_id, logged, cities_name
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    for i in range(4):
        j = 0
        for city_id in cities_id:
            current_timestamp = datetime.datetime.now().isoformat()
            new_data = '[{"timestamp": "'+current_timestamp+'", "value": '+str(random.uniform(0.00,200.00))+'}]'
            print("POST",cities_name[j],"Data:",new_data)
            response = session_request.post('http://252.3.39.61:8041/v1/metric/' + city_id + '/measures', data = new_data, headers = {'Content-Type': 'application/json'})
            print("Response:", response)
            j = j+1
        #sleep in order to don't flood the network
        sleep(5)

if __name__ == "__main__":
    login()
    post()