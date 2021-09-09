"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import zmq

"""
ZMQ Integration Library

It has following classes:
    1. InputPort
        It takes in a socket, socket type and and a topic.
        It can give a data_generator which reads from
        input
        Usage:
        ```
            ip = InputPort(addr="tcp://localhost:5555", topic="asr")
            for data in ip.data_generator():
                do_something(data)
        ```
    2. OutputPort
        It takes in a socket, socket type and a topic.
        It can publish data out.
        Usage:
        ```
            op = OutputPort(addr="tcp://*:5555", topic="asr")
            for data in some_list:
                op.push(data)
            # any event can be sent as second param to push method.
            op.push(b'', 'EOS')
        ```
    3. InputPortWithEvents
        It is similar to input port but it can capture data as well as events.

        a) Event and data are retrieved together
        ```
            ipe = InputPort(addr="tcp://localhost:5555", topic="asr")
            for data,event in ip.data_and_event_generator():
                do_something(data)
                if event:
                    handle_event(event)
        ```
"""


class Port(object):
    def __init__(self, addr, topic, socket_type=zmq.SUB):
        self._stop = False
        self.context = zmq.Context()
        self.topic = topic
        self.socket = self.context.socket(socket_type)

    def stop(self):
        self._stop = True


class InputPort(Port):
    def __init__(self, addr, topic, socket_type=zmq.SUB):
        super().__init__(addr, topic, socket_type=zmq.SUB)
        self.socket.connect(addr)
        if socket_type == zmq.SUB:
            self.socket.setsockopt(zmq.SUBSCRIBE, bytes(self.topic, "utf-8"))

    def data_generator(self):
        while not self._stop:
            a, e = self._recv()
            yield a

    def _recv(self, flags=0):
        topic, array, event = self.socket.recv_multipart(flags=flags)
        return (array, event)


class InputPortWithEvents(InputPort):
    def __init__(self, addr, topic, socket_type=zmq.SUB):
        super().__init__(addr, topic, socket_type=zmq.SUB)
        self.watch_events = {}

    def data_and_event_generator(self):
        while not self._stop:
            array, event = self._recv()
            event_name = event.decode()
            if event_name == "None":
                event_name = None
            yield array, event_name


class OutputPort(Port):
    def __init__(self, addr, topic, socket_type=zmq.PUB):
        super().__init__(addr, topic, socket_type)
        self.socket.bind(addr)

    def push(self, data, event="None"):
        while not self._stop:
            return self.socket.send_multipart(
                (
                    bytes(self.topic, encoding="utf-8"),
                    data,
                    (bytes(event, encoding="utf-8")),
                )
            )
