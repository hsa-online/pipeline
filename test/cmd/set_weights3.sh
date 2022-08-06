curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=dfd2cd54a1ec4a408285f547f6827ea2" \
  -F "data=@../data/dfd2cd54a1ec4a408285f547f6827ea2_098b6e80.b64;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
