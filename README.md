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

## System responses

The system responds to REST calls with JSONs. 
All responses have the `status` and `message` fields. 
The `status` contains a `boolean` value. 
It is required as "partially handled" requests are not responded with HTTP errors codes. 
The `message` contains a `string` value and describes the response.

More about these responses below:

### Prediction results (response to the `/predict` call):

```yaml
{
  "status":  true,
  "message": "0d3c5dffa4374c77a554ed38c9c50296",
  "result": 1.0000178813934326
}
```

| Field | Description |
| --- | --- |
| `status` | Response status: `true` or `false`. |
| `message` | Response message: an Id of the Neural Network used to make this prediction. |
| `result` | Prediction: the sum of two numbers. |

### System status (response to the `/status` call):

```yaml
{
  "status":                   true,
  "message":                  "OK",
  "queue_requests_current":   0,
  "queue_requests_max":       3,
  "req_handling_time_avg_ms": 14.484,
  "workers_count":            1,
  "workers": [
    {
      "address":                  ["192.168.1.133"],
      "nn_id":                    "0d3c5dffa4374c77a554ed38c9c50296",
      "req_handling_time_avg_ms": 11.356,
      "count_values_handled":     1,
      "inference_time_avg_ms":    11.196
    }
  ]
}
```

## Supplementary files 

Weights of the Neural Network can be uploaded to the service from the Gateway. 
Four different sample weights are provided (actually one example contains incorrect data encoded to Base64):

| File | Description |
| --- | --- |
| `000127a35b5f462b8ec68fb4d905ac36_eb191815.b64` | Weights of the NN trained for 20 epochs with batch size 1 |
| `0d3c5dffa4374c77a554ed38c9c50296_66e26224.b64` | Weights of the NN trained for 20 epochs with batch size 2 | 
| `dfd2cd54a1ec4a408285f547f6827ea2_098b6e80.b64` | Weights of the NN trained for 20 epochs with batch size 5 |
| `bad_tensors.b64` | Bad data encoded to Base64 to check service's reaction. |

Provided shell scripts allow to test the system from the command line using cURL utility:

| File | Description |
| --- | --- |
| `predict1.sh` | Predict sum of two numbers: `0.1` and `0.2`. |
| `predict2.sh` | Predict sum of two numbers: `0.446` and `0.554`. |
| `predict_wrong_tensor.sh` | Test the reaction of the system to requesting the sum of three numbers. |
| `set_weights1.sh` | Load sample wights `000127a35b5f462b8ec68fb4d905ac36`. |
| `set_weights2.sh` | Load sample wights `0d3c5dffa4374c77a554ed38c9c50296`. |
| `set_weights3.sh` | Load sample wights `dfd2cd54a1ec4a408285f547f6827ea2`. | 
| `set_weights_bad_base64.sh` | Test the reaction of the system to loading the wights not encoded to Base64. |
| `set_weights_bad_tensors.sh` | Test the reaction of the system to loading as weights an arbitrary data (encoded to Base64). |
| `status.sh` | Get the status of the system. |

