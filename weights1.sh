curl -X PUT -v -H "Content-Type:multipart/form-data" \
  -F "nn_id=000127a35b5f462b8ec68fb4d905ac36" \
  -F "data=@000127a35b5f462b8ec68fb4d905ac36_eb191815.b64;type=application/octet-stream" \
  http://127.0.0.1:54321/set_weights
