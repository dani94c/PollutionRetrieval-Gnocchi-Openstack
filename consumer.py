from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
import requests
from string import Template
import json

#metric_template = Template()
Authorized = False
sessionRequest = requests.session()

def login():
    print("Started login")
    auth = v3.Password(auth_url='http://252.3.39.6:5000/v3',
                    user_id='8bb753b2db8a40dd89c3cce466905716',
                    password='openstack',
                    project_id='674523dc283046d5b1812811e24aa90f')
    sess = session.Session(auth=auth)
    keystone = client.Client(session=sess)
    print("Session obtained")
    token = sess.get_token()
    sessionRequest.headers.update({'X-AUTH-TOKEN': token})
    Authorized = True
    print("Authentication succeded")

def request():
    response = sessionRequest.get('http://252.3.39.61:8041/v1/metric')
    metrics_list = json.loads(response.text)
    for metric in metrics_list:
        if metric['name'] == 'metrica1':
            response = sessionRequest.get('http://252.3.39.61:8041/v1/metric/'+metric['id']+'/measures?refresh=true')
            items = json.loads(response.text)
            print("Items:", items)  
            
if __name__ == "__main__":
    login()
    request()
