#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import numpy as np
import wave
import zmq


def recv_array(socket, flags=0):
    """recv a numpy array"""
    topic, array = socket.recv_multipart(flags=flags)
    array = np.frombuffer(array)
    return array


def main():
    try:
        TOPIC = os.environ["TOPIC"]
    except (KeyError, IndexError):
        TOPIC = "audio"
    try:
        PORT = os.environ["PORT"]
    except (KeyError, IndexError):
        PORT = 6001

    print("Started App")
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://localhost:%s" % PORT)
    print("Connected to Socket")
    topic = bytes("audio", encoding="utf-8")
    socket.setsockopt(zmq.SUBSCRIBE, topic)

    print("Writing data to file ..")

    # since file is opened using "with", no need to close explicitly
    with wave.open("recorded.wav", "wb") as f:
        try:
            f.setframerate(16000)
            f.setnchannels(1)
            f.setsampwidth(2)

            while True:
                # receive frames here
                f.writeframes(recv_array(socket))
        except:
            if f.closed == False:
                f.close()


if __name__ == "__main__":
    main()
