"""
REST API running on a Gateway

"""

import base64
import json

from datetime import datetime
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.datastructures import UploadFile
from starlette.exceptions import HTTPException

from core.app_stats import ApplicationStatistics
from core.msg_helper import MessageHelper

class APIGateway(Starlette):
    """ 
    REST API implementation
    """

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

    async def __status(self, request: Request) -> JSONResponse:
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

    async def __predict(self, request: Request) -> JSONResponse:
        """
        /predict handler
        """
        stats = self.__chan_compute_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        stats = ApplicationStatistics()
        req_handling_time_stats = stats.get_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME)

        time_start = datetime.now()

        try:
            payload = await request.json()
            if 'vector' not in payload and 'data' not in payload:
                # Return 400 Bad Request
                raise HTTPException(status_code=400, detail='vector or data is required')
            s = json.dumps(payload)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail='cannot parse request body')

        await self.__chan_compute_send_api2cluster.send(s)
        async for item in self.__chan_compute_receive_cluster2api:
            time_end = datetime.now()
            time_diff = time_end - time_start
            delta_ms = time_diff.total_seconds() * 1000
            req_handling_time_stats.add_value(delta_ms)

            # Return 200 OK
            return JSONResponse(json.loads(item), status_code=200)

    async def __set_weights(self, request: Request) -> JSONResponse:
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
            raise HTTPException(status_code=400, detail='NN id is required')
        if not isinstance(form['nn_id'], str):
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='NN id should be a string')
        nn_id = form['nn_id']

        if len(nn_id) != 32 or not all(ch in '0123456789abcdef' for ch in nn_id):
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='NN id should contain a lower case UUID string')

        if 'data' not in form:
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='weights data is required')
        if not isinstance(form['data'], UploadFile):
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='weights data should be a file')

        c_type = form['data'].content_type
        if c_type != 'application/octet-stream':
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='weights data should be a binary file')

        data_b64_bytes = await form['data'].read()
        try:
            data = base64.standard_b64decode(data_b64_bytes)
        except base64.binascii.Error as err:
            # Return 400 Bad Request
            raise HTTPException(status_code=400, detail='weights data has wrong format')
       
        await self.__chan_service_send_api2cluster.send(
            MessageHelper.cmd_set_weights(nn_id, data_b64_bytes.decode('utf-8')))
        async for item in self.__chan_service_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(json.loads(item), status_code=200)
