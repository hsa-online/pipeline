"""
REST API running on a Gateway

"""

import json
import http.client as cl

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.datastructures import UploadFile

from core.msg_helper import MessageHelper

class APIGateway(Starlette):
    def __init__(self, 
        chan_service_send_api2cluster, chan_service_receive_cluster2api,
        chan_compute_send_api2cluster, chan_compute_receive_cluster2api):

        super().__init__(routes=[
            Route('/status', self.__status, methods=['GET']),
            Route('/predict', self.__predict, methods=['POST']),
            Route('/set_weights', self.__set_weights, methods=['PUT'])
        ])

        self.__chan_service_send_api2cluster = chan_service_send_api2cluster
        self.__chan_service_receive_cluster2api = chan_service_receive_cluster2api

        self.__chan_compute_send_api2cluster = chan_compute_send_api2cluster
        self.__chan_compute_receive_cluster2api = chan_compute_receive_cluster2api

    async def __status(self, request):
        """
        /status handler
        """
        stats = self.__chan_service_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        await self.__chan_service_send_api2cluster.send(MessageHelper.cmd_status)
        async for item in self.__chan_service_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(json.loads(item), status_code=200)

    async def __predict(self, request):
        """
        /predict handler
        """
        stats = self.__chan_compute_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        try:
            payload = await request.json()
            if 'vector' not in payload and 'data' not in payload:
                # Return 400 Bad Request
                raise cl.HTTPException(status_code=400, detail='vector or data is required')
            s = json.dumps(payload)
        except json.JSONDecodeError:
            raise cl.HTTPException(status_code=400, detail='cannot parse request body')

        await self.__chan_compute_send_api2cluster.send(s)
        async for item in self.__chan_compute_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(json.loads(item), status_code=200)

    async def __set_weights(self, request):
        """
        /set_weights handler
        """
        stats = self.__chan_service_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        form = await request.form()

        if 'nn_id' not in form:
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='NN id is required')
        if not isinstance(form['nn_id'], str):
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='NN id should be a string')
        nn_id = form['nn_id']

        if len(nn_id) != 32 or not all(ch in '0123456789abcdef' for ch in nn_id):
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='NN id should contain a lower case UUID string')

        if 'data' not in form:
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='weights data is required')
        if not isinstance(form['data'], UploadFile):
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='weights data should be a file')

        c_type = form['data'].content_type
        if c_type != 'application/octet-stream':
            # Return 400 Bad Request
            raise cl.HTTPException(status_code=400, detail='weights data should be a binary file')

        # filename = form["data"].filename

        data_b64 = await form['data'].read()
        
        await self.__chan_service_send_api2cluster.send(
            MessageHelper.cmd_set_weights(nn_id, data_b64.decode('utf-8')))
        async for item in self.__chan_service_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(json.loads(item), status_code=200)
