# Pipeline

---

## Python based distributed inference service example ##

This example allows to run NN models inference using a single Gateway with REST and multiple Workers.
Current alpha simulates the inference by computing sums of 2-dimensional vectors passed.

## Requirements

Python 3.9+ (with pynng + trio + starlette + hypercorn + netifaces)

## How to use

Get the Gateway command line help:

```shell
$ python ./gw.py -h 
```

Get the Worker command line help:

```shell
$ python ./worker.py -h 
```

Run Gateway in console:

```shell
$ python ./gw.py 
```

Run one or more Workers (each in its own console):

```shell
$ python ./worker.py
```

Upload weights from file to the service:

```shell
curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=000127a35b5f462b8ec68fb4d905ac36" \
  -F "data=@../data/000127a35b5f462b8ec68fb4d905ac36_eb191815.b64;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
```

Predict the sum of two numbers (from [0.0,1.0] interval) with the service:

```shell
curl -X POST http://127.0.0.1:54321/predict \
   -H 'Content-Type: application/json' \
   -d '{"vector": [0.3, 0.7]}'
```

Get the status of the service:

```shell
curl -X GET http://127.0.0.1:54321/status
```

## Supplementary files 

Weights of the Neural Network can be uploaded to the service from the Gateway. 
Four different sample weights are provided (actually one example contains incorrect data encoded to Base64).

| File | Description |
| --- | --- |
| `000127a35b5f462b8ec68fb4d905ac36_eb191815.b64` | weights of the NN trained for 20 epochs with batch size 1 |
| `0d3c5dffa4374c77a554ed38c9c50296_66e26224.b64` | weights of the NN trained for 20 epochs with batch size 2 | 
| `dfd2cd54a1ec4a408285f547f6827ea2_098b6e80.b64` | weights of the NN trained for 20 epochs with batch size 5 |
| `bad_tensors.b64` | bad data encoded to Base64 to check service's reaction. |
