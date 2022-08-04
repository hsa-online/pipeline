"""
Asynchronous tasks for both the Gateway and Worker.

"""

import json
import pynng
import trio

from core.msg_helper import MessageHelper
from core.utility import get_local_ips

async def task_gw_service(channel_send, channel_receive, surveyor):
    async for item in channel_receive:
        surveyor.survey_time = 500
        await surveyor.asend(item.encode())

        results = []
        while True:
            try:
                response = await surveyor.arecv()
                results.append(response.decode("utf-8"))
            except pynng.Timeout:
                break
        response = MessageHelper.api_response_status(results)
        await channel_send.send(response)

async def task_gw_predict(channel_send, channel_receive, sock):
    async for item_str in channel_receive:
        item_bytes = item_str.encode()
        await sock.asend(item_bytes)

        result_bytes = await sock.arecv()
        result_str = result_bytes.decode("utf-8")
        result = json.loads(result_str) 

        response = MessageHelper.api_response_predict(result)
        await channel_send.send(response)

async def task_work_service(responder):
    while True:
        # TODO: Remove debug output
        print(f'[service waiting...]')
        item_bytes = await responder.arecv()
        item_str = item_bytes.decode("utf-8")

        # TODO: Remove debug output
        print(f'item received: {item_str}')

        ips = get_local_ips()
        response = MessageHelper.cmd_response_status(ips)
        await responder.asend(response.encode())

async def task_work_predict(sock):
    while True:
        # TODO: Remove debug output
        print(f'[predict waiting...]')

        item_bytes = await sock.arecv()
        item_str = item_bytes.decode("utf-8")

        # TODO: Remove debug output
        print(f'item received: {item_str}')

        item = json.loads(item_str)
        if 'vector' in item:
            v = item['vector']
        else: 
            # TODO: Unpack 'data' to vector
            v = None

        total = sum(v)
        # TODO: Remove debug output
        print(f'total={total}')

        response = MessageHelper.cmd_response_predict(total)
        await sock.asend(response.encode())
