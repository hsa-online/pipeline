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

Several shell scripts are provided to simplify the testing. See [Shell scripts](#shell-scripts).

## System responses

The system responds to REST calls with JSONs. 
All responses have the `status` and `message` fields. 
The `status` contains a `boolean` value. 
It is required as "partially handled" requests are not responded with HTTP errors codes. 
The `message` contains a `string` value and describes the response.

More about these responses below:

### Weights loading results (response to the `/set_weights` call):

Contains results of new weights loading to the system.

If new weights were successfully loaded:

```yaml
{
  "status":        true,
  "message":       "OK",
  "workers_count": 1,
  "workers": [
    {
      "result": true
    }
  ]
}
```

| Field | Description |
| --- | --- |
| `status` | Response status: `true` for successful load. |
| `message` | Response message. |
| `workers_count` | Number of Workers which actually loaded the new weights. |
| `workers` | An array of workers. Each object from this array contains a data from single Worker. |
| `workers[i].result` | This Worker's weights loading result. |

When the weights are incorrect, system responds with this answer:

```yaml
{
  "status":        false,
  "message":       "One or more workers were failed with weights loading",
  "workers_count": 1,
  "workers": [
    {
      "result": false,
      "trace":  "VHJhY2ViYWNrICh ... cmVkaWN0LnNoCg=="
    }
  ]
}
```

Please note that in the example above the `trace` field is partially cut.

| Field | Description |
| --- | --- |
| `status` | Response status: `false`. |
| `message` | Response message: error description. |
| `workers_count` | Number of Workers which actually responded to the call. |
| `workers` | An array of workers. Each object from this array contains a data from single Worker. |
| `workers[i].result` | This Worker's weights loading result. |
| `workers[i].trace` | When the `result` is `false`, contains a Base64 encoded stack trace of the Worker. |

### Prediction results (response to the `/predict` call):

Contains prediction results.

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
| `message` | Response message: an `id` of the Neural Network used to make this prediction. |
| `result` | Prediction: the sum of two numbers. |


When prediction is failed the `message` field will contain Base64 encoded stack trace describing what's happened.
Please note that in the example below the `message` field is partially cut.

```yaml
{
  "status":  false,
  "message": "VHJhY2ViYW...hbmQgMngyMCkK",
  "result":  0.0
}
```

| Field | Description |
| --- | --- |
| `status` | Response status: `false`. |
| `message` | Response message: Base64 encoded stack trace of the system. |
| `result` | Prediction: 0.0 for failed prediction. |

### System status (response to the `/status` call):

Contains an overall status of the system and all its Workers.

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
      "count_requests_handled":   1,
      "inference_time_avg_ms":    11.196
    }
  ]
}
```

| Field | Description |
| --- | --- |
| `status` | Response status: `true` or `false`. |
| `message` | Response message. |
| `queue_requests_current` | Number of unhandled requests in the requests queue. |
| `queue_requests_max` | Maximum size of the requests queue. |
| `req_handling_time_avg_ms` | Average request handling time in the system (in milliseconds). |
| `workers_count` | Number of Workers in the system. |
| `workers` | An array of workers. Each object from this array contains a data from single Worker. |
| `workers[i].address` | An IP address of this Worker. Value is returned as array as the host may have more than one network addresses. |
| `workers[i].nn_id` | An `id` of the Neural Network loaded to this Worker. |
| `workers[i].req_handling_time_avg_ms` | Average request handling time for this Worker (in milliseconds). |
| `workers[i].count_requests_handled` | Count of requests handled by this Worker. |
| `workers[i].inference_time_avg_ms` | Average inference time for this Worker (in milliseconds). |

## Supplementary files 

### Weights

Weights of the Neural Network can be uploaded to the service from the Gateway. 
Four different sample weights are provided (actually one example contains incorrect data encoded to Base64):

| File | Description |
| --- | --- |
| `000127a35b5f462b8ec68fb4d905ac36_eb191815.b64` | Weights of the NN trained for 20 epochs with batch size 1 |
| `0d3c5dffa4374c77a554ed38c9c50296_66e26224.b64` | Weights of the NN trained for 20 epochs with batch size 2 | 
| `dfd2cd54a1ec4a408285f547f6827ea2_098b6e80.b64` | Weights of the NN trained for 20 epochs with batch size 5 |
| `bad_tensors.b64` | Bad data encoded to Base64 to check service's reaction. |

### Shell scripts

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

