import json

from core.cls_property import classproperty

class MessageHelper:
    @classproperty
    def cmd_status(cls) -> str:
        cmd = {}
        cmd['cmd'] = 'status'
        return json.dumps(cmd)

    @staticmethod
    def cmd_response_status(addr) -> str:
        cmd_resp = {}
        cmd_resp['address'] = addr
        return json.dumps(cmd_resp)

    @staticmethod
    def cmd_response_predict(total) -> str:
        cmd_resp = {}
        cmd_resp['total'] = total
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
    def api_response_predict(result) -> str:
        resp = {}
        resp['status'] = True
        resp['message'] = 'OK'
        resp['result'] = result
        return json.dumps(resp)
