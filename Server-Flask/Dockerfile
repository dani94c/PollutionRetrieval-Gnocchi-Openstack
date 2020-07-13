FROM ubuntu 
RUN apt-get update && apt-get install -y python3 python3-pip 
RUN pip3 install flask numpy requests keystoneauth1 python-keystoneclient

ADD ./server-flask.py /root/

EXPOSE 8080

CMD ["/usr/bin/python3","/root/server-flask.py"]
