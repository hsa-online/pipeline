"""
Both the REST API responses encoder and service internal commands encoder.

"""

import json

from typing import Any, List, Dict

from core.cls_property import classproperty
from core.cmd import Command

class MessageHelper:
    @classproperty
    def cmd_status(cls) -> str:
        cmd = {}
        cmd['cmd'] = Command.STATUS
        return json.dumps(cmd)

    @staticmethod
    def cmd_response_status(
        addr: str, 
        nn_id: str, 
        req_handling_time_ms: float, 
        count_values_handled: int, 
        inference_time_ms: float) -> str:

        cmd_resp = {}
        cmd_resp['address'] = addr
        cmd_resp['nn_id'] = nn_id
        cmd_resp['req_handling_time_avg_ms'] = req_handling_time_ms
        cmd_resp['count_requests_handled'] = count_values_handled
        cmd_resp['inference_time_avg_ms'] = inference_time_ms
        return json.dumps(cmd_resp)

    @staticmethod
    def cmd_set_weights(nn_id: str, data: str) -> str:
        cmd = {}
        cmd['cmd'] = Command.SET_WEIGHTS
        cmd['nn_id'] = nn_id
        cmd['data'] = data
        return json.dumps(cmd)

    @staticmethod
    def cmd_response_set_weights(res_status: bool, res_trace_str: str) -> str:
        cmd_resp = {}
        cmd_resp['result'] = res_status
        if not res_status and res_trace_str != "": 
            cmd_resp['trace'] = res_trace_str
        return json.dumps(cmd_resp)

    @staticmethod
    def cmd_response_predict(res) -> str:
        cmd_resp = {}
        cmd_resp['status'] = res[0]
        cmd_resp['message'] = res[1]
        cmd_resp['result'] = res[2]
        return json.dumps(cmd_resp)

    @classproperty
    def api_response_server_busy(cls) -> str:
        resp = {}
        resp['status'] = False
        resp['message'] = 'Server is busy'
        return json.dumps(resp)

    @staticmethod
    def api_response_status(
        queue_requests_current: int,
        queue_requests_max: int, 
        req_handling_time_avg_ms: float, 
        results: List[Any]) -> str:

        resp = {}
        resp['status'] = True
        resp['message'] = 'OK'
        resp['queue_requests_current'] = queue_requests_current
        resp['queue_requests_max'] = queue_requests_max
        resp['req_handling_time_avg_ms'] = req_handling_time_avg_ms
        resp['workers_count'] = len(results)
        resp['workers'] = results
        return json.dumps(resp)

    @staticmethod
    def api_response_set_weights(overall_result: bool, results: List[Any]) -> str:
        resp = {}
        if overall_result:
          resp['status'] = True
          resp['message'] = 'OK'
        else:
          resp['status'] = False
          resp['message'] = 'One or more workers were failed with weights loading'
        resp['workers_count'] = len(results)
        resp['workers'] = results
        return json.dumps(resp)

    @staticmethod
    def api_response_predict(result: Dict[str, Any]) -> str:
        resp = {}
        resp['status'] = result['status']
        resp['message'] = result['message']
        resp['result'] = result['result']
        return json.dumps(resp)
