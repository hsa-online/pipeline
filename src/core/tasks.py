"""
Asynchronous tasks for both the Gateway and Worker.

"""

import base64
import json
import pynng
import trio

from datetime import datetime

from core.app_stats import ApplicationStatistics
from core.cmd import Command
from core.inferencer import Inferencer
from core.msg_helper import MessageHelper
from core.utility import get_local_ips

async def task_gw_service(channel_send, channel_receive, channel_compute_send, surveyor):
    """
    Gateway task to handle service requests
    """

    async for item in channel_receive:
        cmd = json.loads(item)['cmd']

        if cmd == Command.SET_WEIGHTS:
            surveyor.survey_time = 3000
            await surveyor.asend(item.encode())

            overall_result = True
            results = []
            while True:
                try:
                    response_bytes = await surveyor.arecv()
                    response_str = response_bytes.decode('utf-8')
                    response = json.loads(response_str)
                    if not response['result']:
                        overall_result = False
                    results.append(response)
                except pynng.Timeout:
                    break
            response = MessageHelper.api_response_set_weights(overall_result, results)
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

            stats = ApplicationStatistics()
            req_handling_time_stats = stats.get_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME)

            stats_chan = channel_compute_send.statistics()
            queue_requests_current = stats_chan.current_buffer_used 
            queue_requests_max = stats_chan.max_buffer_size

            response = MessageHelper.api_response_status(
                queue_requests_current, 
                queue_requests_max, 
                req_handling_time_stats.average, 
                results)

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

    stats = ApplicationStatistics()
    inference_time_stats = stats.get_stats_holder(ApplicationStatistics.NN_INFERENCE_TIME)
    req_handling_time_stats = stats.get_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME)

    while True:
        # TODO: Remove debug output
        print(f'[Service is waiting...]')

        cmd_bytes = await responder.arecv()
        cmd_str = cmd_bytes.decode('utf-8')
        cmd = json.loads(cmd_str)

        if cmd['cmd'] == Command.STATUS:
            ips = get_local_ips()
            response = MessageHelper.cmd_response_status(
                ips, 
                inferencer.nn_id, 
                req_handling_time_stats.average,
                inference_time_stats.count_values_handled, 
                inference_time_stats.average)
        elif cmd['cmd'] == Command.SET_WEIGHTS:
            nn_id = cmd['nn_id']
            data_str = cmd['data']
            data = base64.standard_b64decode(data_str.encode())

            res_list = inferencer.load_weights(nn_id, data)

            res_status = res_list[0]
            res_trace_str = res_list[1]
            if not res_status:
                res_trace_str = base64.standard_b64encode(
                    res_trace_str.encode()).decode('utf-8')

            response = MessageHelper.cmd_response_set_weights(res_status, res_trace_str)

        await responder.asend(response.encode())

async def task_work_predict(sock):
    """
    Worker task to handle the 'predict' request
    """

    inferencer = Inferencer()

    stats = ApplicationStatistics()
    inference_time_stats = stats.get_stats_holder(ApplicationStatistics.NN_INFERENCE_TIME)
    req_handling_time_stats = stats.get_stats_holder(ApplicationStatistics.REQ_HANDLING_TIME)

    while True:
        item_bytes = await sock.arecv()

        time_start_req = datetime.now()

        item_str = item_bytes.decode('utf-8')

        item = json.loads(item_str)
        if 'vector' in item:
            v = item['vector']
        else: 
            # TODO: Unpack 'data' to vector
            v = None

        time_start = datetime.now()

        res = inferencer.predict(v)

        time_end = datetime.now()
        time_diff = time_end - time_start
        delta_ms = time_diff.total_seconds() * 1000
        inference_time_stats.add_value(delta_ms)

        response = MessageHelper.cmd_response_predict(res)
        response_bytes = response.encode()

        time_end_req = datetime.now()
        time_diff_req = time_end_req - time_start_req
        delta_req_ms = time_diff_req.total_seconds() * 1000
        req_handling_time_stats.add_value(delta_req_ms)

        await sock.asend(response_bytes)
