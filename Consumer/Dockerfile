FROM ubuntu
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install numpy requests keystoneauth1 python-keystoneclient

ADD ./consumer.py /root/

CMD ["/usr/bin/python3","/root/consumer.py"]