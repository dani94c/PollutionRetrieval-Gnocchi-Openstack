# Pollution Retrieval Application with GnocchiDB and OpenStack platform and Flask interface on Docker containers

## Code Execution
In order to execute the code with the containers it is necessary to build the images of the container starting from the Python code and the Dockerfiles:

```
docker build -t producer ./Producer
docker build -t consumer ./Consumer
docker build -t server-flask ./Server-Flask
```

Then you can run the cointainer:

```
docker run -it consumer
docker run -it producer
docker run -p 8080:8080 -it server-flask
```

## Credits
D. Comola, E. Petrangeli, G. Alvaro, L. Fontanelli