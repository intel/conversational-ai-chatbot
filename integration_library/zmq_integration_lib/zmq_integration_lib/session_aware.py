"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from zmq_integration_lib import InputPortWithEvents, OutputPort
from zmq_integration_lib import RPCClient, supported_cmds
import json
import base64


"""
#Reciever

```
from zmq_integration_lib import get_inpad
ip = get_inpad('tcp://localhost:6000', 'hello', 'tcp://localhost:6900')
for d,e in ip.data_and_event_generator():
    print (d)
```

# First Sender (with no inpad)

```
from zmq_integration_lib import get_outpad
sid = '4a501b51317e2c8f4a0fd7831d3e09dc'
op = get_outpad("tcp://*:6000", "hello")
op.update_session_id(sid)
op.push(b'Hi boy')
```

# Subsequent Senders (apps which ahve both inpad and outpad)
# no explicit session id is required, it is handled internally by the module

```
from zmq_integration_lib.session_aware import get_outpad
op = get_outpad("tcp://*:6000", "hello")
op.push(b'Hi boy')
```

Module has a databus which recieved session id from inpad and provides it to outpad. So the application can remain oblivious of session_id. inpad verifies the session id which rpchost.


"""


class _SessionAwareINPAD(InputPortWithEvents):
    subscibers = []

    def _notify_session_id_update(self, session_id):
        for ons in self.subscibers:
            ons(session_id)

    def _verify_session_id(self, session_id):
        self._notify_session_id_update(session_id)
        # Notify session_id before verifying
        return self.rpcproxy.verify(session_id)

    def _get_session_id_from_data(self, data):
        data = data.decode()
        # print ('data recieved: {} '.format(data))
        d_dict = json.loads(data)
        return d_dict["session_id"]

    def _get_data(self, data):
        data = data.decode()
        d_dict = json.loads(data)
        # data field of json is a base64 encoded string
        return base64.decodebytes(bytes(d_dict["data"], encoding="utf-8"))

    def set_rpc_host(self, addr):
        self.rpcproxy = RPCClient(addr, supported_cmds)

    def set_session_update_callback(self, notifyme):
        self.subscibers.append(notifyme)

    def data_and_event_generator(self):
        for data, event in super().data_and_event_generator():
            session_id = self._get_session_id_from_data(data)
            if self._verify_session_id(session_id):
                yield self._get_data(data), event


class _SessionAwareOUTPAD(OutputPort):
    session_id = None

    def update_session_id(self, session_id):
        self.session_id = session_id

    def _append_session_id_to_data(self, data):
        data_str = base64.b64encode(data).decode()
        dbuff_dict = {"data": data_str, "session_id": self.session_id}
        return bytes(json.dumps(dbuff_dict), encoding="utf-8")

    def push(self, data, event="None"):
        d = self._append_session_id_to_data(data)
        if d is not None:
            return super().push(d, event)


class _DataBus(object):
    input_pad = None
    output_pad = None
    session_id = None
    callback = None

    def update_sessionid(self, session_id):
        self.session_id = session_id
        # Notify the session_id change to outpad
        if self.callback:
            self.callback(session_id)

    def add_inputport(self, inp):
        self.input_pad = inp

    def add_outputport(self, outp):
        self.output_pad = outp
        self.callback = outp.update_session_id

    def add_rpcclient(self, rcaddr):
        pass

    def get_session_aware_inpad(self):
        return self.input_pad

    def get_session_aware_outpad(self):
        return self.output_pad


# Create a data bus and input output pads
db = _DataBus()

# Public API of module


def get_inpad(addr, topic, vaddr):
    ipp = _SessionAwareINPAD(addr, topic)
    ipp.set_rpc_host(vaddr)
    ipp.set_session_update_callback(db.update_sessionid)
    # set rpc host on inpad
    db.add_inputport(ipp)
    return db.get_session_aware_inpad()


def get_outpad(addr, topic):
    opp = _SessionAwareOUTPAD(addr, topic)
    db.add_outputport(opp)
    return db.get_session_aware_outpad()
