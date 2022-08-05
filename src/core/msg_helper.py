import json

from typing import Any, Dict

from core.cls_property import classproperty
from core.cmd import Command

class MessageHelper:
    @classproperty
    def cmd_status(cls) -> str:
        cmd = {}
        cmd['cmd'] = Command.STATUS
        return json.dumps(cmd)

    @staticmethod
    def cmd_response_status(addr) -> str:
        cmd_resp = {}
        cmd_resp['address'] = addr
        return json.dumps(cmd_resp)

    @staticmethod
    def cmd_set_weights(nn_id, data) -> str:
        cmd = {}
        cmd['cmd'] = Command.SET_WEIGHTS
        cmd['nn_id'] = nn_id
        cmd['data'] = data
        return json.dumps(cmd)

    @staticmethod
    def cmd_response_set_weights(res) -> str:
        cmd_resp = {}
        cmd_resp['result'] = res
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
    def api_response_status(results) -> str:
        resp = {}
        resp['status'] = True
        resp['message'] = 'OK'
        resp['workers_count'] = len(results)
        resp['workers'] = results
        return json.dumps(resp)

    @staticmethod
    def api_response_set_weights(results) -> str:
        resp = {}
        resp['status'] = True
        resp['message'] = 'OK'
        resp['workers_count'] = len(results)
        resp['workers'] = results
        return json.dumps(resp)

    @staticmethod
    def api_response_predict(result: Dict[str, Any]) -> str:
        print(f'>>>>>>>>>>>{result}')
        resp = {}
        resp['status'] = result['status']
        resp['message'] = result['message']
        resp['result'] = result['result']
        return json.dumps(resp)
