curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=00000000000000000000000000000000" \
  -F "data=@set_weights1.sh;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
