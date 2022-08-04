# Pipeline

---

## Python based distributed inference service example ##

This example allows to run NN models inference using a single Gateway with REST and multiple Workers.
Current alpha simulates the inference by computing sums of vectors passed.

## Requirements

Python 3.9+ (with pynng + trio + starlette + hypercorn)

## How to use

Get help:

```shell
$ python ./gw.py -h 
```

Run Gateway in console:

```shell
$ python ./gw.py 
```

Run one or more Workers (each in its own console):

```shell
$ python ./worker.py
```

Call the service:

```shell
curl -X POST http://127.0.0.1:54321/predict \
   -H 'Content-Type: application/json' \
   -d '{"vector": [100, 200]}'
```
