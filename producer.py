from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client
import requests
from string import Template
import datetime
import json

Authorized = False
sessionRequest = requests.session()
metrics = Template('{$all_metrics}')
metric_id = ''
#metric_template = Template()

# Login function - Obtain the token with Keystone
def login():
    global metric_id
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
    # Retrieving the metric-id
    response = sessionRequest.get('http://252.3.39.61:8041/v1/metric')
    print("Response nel login:", response)
    metrics_list = json.loads(response.text)
    for metric in metrics_list:
        if metric['name'] == 'metrica1':
           metric_id = metric['id']  
           break   
    print("Metric id:", metric_id)

# Post function in order to insert a new value for the metric
def post():
    global metric_id
    current_timestamp = datetime.datetime.now().isoformat()
    for i in range(61):
        mydata = '[{"timestamp": "'+current_timestamp+'", "value": '+str(i)+'}]'
        print("mydata:", mydata)
        response = sessionRequest.post('http://252.3.39.61:8041/v1/metric/' + metric_id + '/measures', data = mydata, headers = {'Content-Type': 'application/json'})
        print("Response:", response)

if __name__ == "__main__":
    login()
    post()
