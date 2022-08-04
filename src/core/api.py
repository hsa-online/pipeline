"""
REST API

"""

import json
import http.client as cl

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from core.msg_helper import MessageHelper

class APIGateway(Starlette):
    def __init__(self, 
        chan_service_send_api2cluster, chan_service_receive_cluster2api,
        chan_compute_send_api2cluster, chan_compute_receive_cluster2api):

        super().__init__(routes=[
            Route('/status', self.__status, methods=['GET']),
            Route('/predict', self.__predict, methods=['POST'])
        ])

        self.__chan_service_send_api2cluster = chan_service_send_api2cluster
        self.__chan_service_receive_cluster2api = chan_service_receive_cluster2api

        self.__chan_compute_send_api2cluster = chan_compute_send_api2cluster
        self.__chan_compute_receive_cluster2api = chan_compute_receive_cluster2api

    async def __status(self, request):
        stats = self.__chan_service_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        await self.__chan_service_send_api2cluster.send(MessageHelper.cmd_status)
        async for item in self.__chan_service_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(item, status_code=200)

    async def __predict(self, request):
        try:
            payload = await request.json()
            if 'vector' not in payload and 'data' not in payload:
                raise cl.HTTPException(status_code=400, detail="vector or data is required")
            s = json.dumps(payload)
        except json.JSONDecodeError:
            raise cl.HTTPException(status_code=400, detail="cannot parse request body")

        stats = self.__chan_compute_send_api2cluster.statistics()
        if stats.current_buffer_used == stats.max_buffer_size:
            # Return 503 Service Unavailable
            return JSONResponse(MessageHelper.response_server_busy, status_code=503)

        await self.__chan_compute_send_api2cluster.send(s)
        async for item in self.__chan_compute_receive_cluster2api:
            # Return 200 OK
            return JSONResponse(item, status_code=200)
