"""
Asynchronous tasks for both the Gateway and Worker.

"""

import base64
import json
import pynng
import trio

from core.cmd import Command
from core.inferencer import Inferencer
from core.msg_helper import MessageHelper
from core.utility import get_local_ips

async def task_gw_service(channel_send, channel_receive, surveyor):
    """
    Gateway task to handle service requests
    """
    async for item in channel_receive:
        cmd = json.loads(item)['cmd']

        if cmd == Command.SET_WEIGHTS:
            surveyor.survey_time = 3000
            await surveyor.asend(item.encode())

            results = []
            while True:
                try:
                    response = await surveyor.arecv()
                    results.append(json.loads(response.decode('utf-8')))
                except pynng.Timeout:
                    break
            response = MessageHelper.api_response_set_weights(results)
        elif cmd == Command.STATUS:
            surveyor.survey_time = 500
            await surveyor.asend(item.encode())

            results = []
            while True:
                try:
                    response = await surveyor.arecv()
                    results.append(json.loads(response.decode('utf-8')))
                except pynng.Timeout:
                    break
            response = MessageHelper.api_response_status(results)

        await channel_send.send(response)

async def task_gw_predict(channel_send, channel_receive, sock):
    """
    Gateway task to handle the 'predict' request
    """
    async for item_str in channel_receive:
        item_bytes = item_str.encode()
        await sock.asend(item_bytes)

        result_bytes = await sock.arecv()
        result_str = result_bytes.decode('utf-8')
        result = json.loads(result_str) 

        response = MessageHelper.api_response_predict(result)
        await channel_send.send(response)

async def task_work_service(responder):
    """
    Worker task to handle service requests
    """
    inferencer = Inferencer()
    while True:
        # TODO: Remove debug output
        print(f'[service waiting...]')
        cmd_bytes = await responder.arecv()
        cmd_str = cmd_bytes.decode('utf-8')
        cmd = json.loads(cmd_str)
        if cmd['cmd'] == Command.STATUS:
            # TODO: Remove debug output
            print(f'item received: {item_str}')

            ips = get_local_ips()
            response = MessageHelper.cmd_response_status(ips)
        elif cmd['cmd'] == Command.SET_WEIGHTS:
            nn_id = cmd['nn_id']
            data_str = cmd['data']
            data = base64.standard_b64decode(data_str.encode())
            res = inferencer.load_weights(nn_id, data)
            response = MessageHelper.cmd_response_set_weights(res)

        await responder.asend(response.encode())

async def task_work_predict(sock):
    """
    Worker task to handle the 'predict' request
    """

    inferencer = Inferencer()
    while True:
        # TODO: Remove debug output
        print(f'[predict is waiting...]')

        item_bytes = await sock.arecv()
        item_str = item_bytes.decode('utf-8')

        # TODO: Remove debug output
        print(f'item received: {item_str}')

        item = json.loads(item_str)
        if 'vector' in item:
            v = item['vector']
        else: 
            # TODO: Unpack 'data' to vector
            v = None

        res = inferencer.predict(v)
        # TODO: Remove debug output
        print(f'res={res}')

        response = MessageHelper.cmd_response_predict(res)
        await sock.asend(response.encode())
