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
sessionRequest = requests.session()
citiesId = []
                    
# Login function - Obtain the token with Keystone
def login():
    global citiesId, logged
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
    # Retrieving the metric-id
    response = sessionRequest.get('http://252.3.39.61:8041/v1/metric')
    print("Response nel login:", response)
    citiesId.clear()
    metrics_list = json.loads(response.text)
    for metric in metrics_list:
        citiesId.append(metric['id'])

# Post function in order to insert a new value for the metric
def post():
    global citiesId, logged
    if(logged == False):
        print("Authentication failed. Retry login")
        login()
    while(True):
        for cityId in citiesId:
            current_timestamp = datetime.datetime.now().isoformat()
            mydata = '[{"timestamp": "'+current_timestamp+'", "value": '+str(random.uniform(0.00,200.00))+'}]'
            print("POST",cityId,"mydata:",mydata)
            response = sessionRequest.post('http://252.3.39.61:8041/v1/metric/' + cityId + '/measures', data = mydata, headers = {'Content-Type': 'application/json'})
            print("Response:", response)
        sleep(5)

if __name__ == "__main__":
    login()
    post()
