curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=11111111111111111111111111111111" \
  -F "data=@../data/bad_tensors.b64;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
