curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=0d3c5dffa4374c77a554ed38c9c50296" \
  -F "data=@../data/0d3c5dffa4374c77a554ed38c9c50296_66e26224.b64;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
