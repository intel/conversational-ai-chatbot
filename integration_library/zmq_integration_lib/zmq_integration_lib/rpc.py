"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import json
import zmq
import logging as log

"""
RPC Server

>>> def verify(sha):
        return True
>>> import zmq_integration_lib as z
>>> r=z.RPCServer('tcp://*:6900', z.supported_cmds)
>>> r.set_handler('verify', verify)
>>> r.run()

RPC Client

>>> import zmq_integration_lib as z
>>> c=z.RPCClient('tcp://localhost:6900', z.supported_cmds)
>>> c.verify('sometext')

"""

# The supported rpcs are listed as dictionaries and included both with servers and clients.
supported_cmds = {
    "verify": '{"jsonrpc": "2.0", "method": "verify", "params":{"session_id": "empty" }, "id":"1"}',
    "get_token": '{"jsonrpc": "2.0", "method": "get_token", "params":{}, "id":"2" }',
    "logout": '{"jsonrpc": "2.0", "method": "logout", "params":{"token": "empty" }, "id":"3" }',
}


class ClientConn(object):
    def __init__(self, addr):
        self._addr = addr
        self.context = zmq.Context()
        self._socket = self.context.socket(zmq.REQ)

    def sync_call(self, jsonrpc_req_str):
        self._socket.connect(self._addr)
        self._socket.send(bytes(jsonrpc_req_str, encoding="utf-8"))
        resp = self._socket.recv()
        return resp.decode()


class RPCClient(object):
    def __init__(self, addr, supported_cmds):
        self._conn = ClientConn(addr)
        self._supported_cmds = supported_cmds

    def _parse_json_response(self, resp):
        scd = json.loads(resp)
        if "error" in scd.keys():
            raise ValueError
        if "result" in scd.keys():
            return scd["result"]

    def _command(self, cmd, args=""):
        if not cmd in self._supported_cmds.keys():
            raise ValueError
        scd = json.loads(self._supported_cmds[cmd])
        if scd["params"]:
            scd["params"] = args
        scds = json.dumps(scd)
        resp = self._conn.sync_call(scds)
        return self._parse_json_response(resp)

    def verify(self, session_id):
        ret = self._command("verify", session_id)
        return ret

    def get_token(self):
        token = self._command("get_token")
        return token

    def logout(self, token):
        token = self._command("logout", token)
        return token


class ServerConn(object):
    def __init__(self, addr):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(addr)

    def run(self, command_handler):
        while True:
            out = self.socket.recv()
            resp = command_handler(out.decode())
            self.socket.send(bytes(resp, encoding="utf-8"))


class RPCServer(object):
    def __init__(self, addr, supported_cmds):
        self.handlers = dict()
        self.conn = ServerConn(addr)
        self.supported_cmds = supported_cmds

    def set_handler(self, cmd, handler):
        if cmd in self.supported_cmds.keys():
            self.handlers[cmd] = handler
        else:
            raise ValueError

    def _json_response(self, id, data, error=False):
        response_template = '{"jsonrpc": "2.0", "result": {} , "id": {} }'
        response_error_template = '{"jsonrpc": "2.0", "error": {} , "id": {} }'
        if not error:
            k = json.loads(response_template)
            k["result"] = data
            k["id"] = id
            return json.dumps(k)

        k = json.loads(response_error_template)
        k["error"] = data
        k["id"] = id
        return json.dumps(k)

    def _command_handler(self, jsorrpc_request_str):
        scd = json.loads(jsorrpc_request_str)
        try:
            cmd = scd["method"]
            args = scd["params"]
            if args:
                ret = self.handlers[cmd](args)
            else:
                ret = self.handlers[cmd]()
            retv = self._json_response(scd["id"], ret)
        except (KeyError, IndexError):
            retv = self._json_response(scd["id"], "Command Not Supported", error=True)
        return retv

    def run(self):
        return self.conn.run(self._command_handler)
