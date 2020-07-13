# Pollution Retrieval Application with GnocchiDB and OpenStack platform and Flask interface on Docker containers

In order to execute the code with  the containers it is necessary to build the images of the container starting from the Python code.

''''shell
docker build -t producer ./Producer
''''

''''shell
docker build -t consumer ./Consumer
''''

''''shell
docker build -t server-flask ./Server-Flask
''''

Then you can run the cointainer

''''shell
docker run -it consumer
''''

''''shell
docker run -it producer
''''

''''shell
docker run -p 8080:8080 -it server-flask
''''

