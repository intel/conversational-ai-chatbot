"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import os
import logging
from envparse import Env
from zmq_integration_lib import InputPortWithEvents, get_outpad
from threading import Thread, RLock


def display_help():
    print("The application needs the following environment variables.")
    print("INPUT_ADDR, INPUT_TOPIC, OUTPUT_ADDR, OUTPUT_TOPIC")
    print("Please set the variables and try again.")


class LoginSessionWatcher(object):
    _session_valid = None
    _session_id = None
    _lock = None

    def __init__(self, input_addr, input_topic):
        self._lock = RLock()
        self.input_port = InputPortWithEvents(input_addr, input_topic)

    def run_thread(self):
        t = Thread(target=self._watch_for_session_change, daemon=True)
        t.start()

    def _watch_for_session_change(self):
        print("Thread running")
        for id, event in self.input_port.data_and_event_generator():
            if event == "signin":
                self._session_valid = True
                self._session_id = id
            elif event == "signout":
                self._session_valid = False
                print("got a signout event")
                self._session_id = None

    @property
    def session_valid(self):
        with self._lock:
            return self._session_valid

    @property
    def session_id(self):
        with self._lock:
            try:
                return self._session_id.decode()
            except Exception:
                return self._session_id


def get_wave_files():
    file_list = WAVE_FILES.split(",")
    full_path = lambda x: os.path.join(WAVE_PATH, x)
    return tuple(map(full_path, file_list))


def get_login_watcher():
    lw = LoginSessionWatcher(INPUT_ADDR, INPUT_TOPIC)
    lw.run_thread()
    return lw


def get_output_port():
    Outport = get_outpad(OUTPUT_ADDR, OUTPUT_TOPIC)
    return Outport


def _validate_env_addr_variable(INPUT_ADDR, OUTPUT_ADDR, AUTHZ_SERVER_ADDR):
    for variable in [INPUT_ADDR, OUTPUT_ADDR, AUTHZ_SERVER_ADDR]:
        if (
            not (type(variable) == str)
            or not (len(variable.split()) == 1)
            or not (("tcp" in variable.split(":")) or ("ipc" in variable.split(":")))
        ):
            raise ValueError("Please check {} address".format(variable))


def _validate_env_topic_variable(INPUT_TOPIC, OUTPUT_TOPIC):
    for variable in [INPUT_TOPIC, OUTPUT_TOPIC]:
        if not (type(variable) == str) or not (len(variable.split()) == 1):
            raise ValueError("Please check {} topic".format(variable))


def _validate_env_log_level_variable(LOG_LEVEL):
    if not LOG_LEVEL.lower() in ["info", "error", "debug"] or not (
        len(LOG_LEVEL.split()) == 1
    ):
        raise ValueError("Please provide correct Log level")


def _read_env_variables():
    # Can set schema
    env = Env(
        OUTPUT_ADDR=str,
        OUTPUT_TOPIC=str,
        INPUT_TOPIC=str,
        INPUT_ADDR=str,
        AUTHZ_SERVER_ADDR=str,
        WAVE_FILES=str,
        LOG_LEVEL=dict(cast=str, default="ERROR"),
        WAVE_PATH=str,
    )

    OUTPUT_ADDR = env("OUTPUT_ADDR")
    OUTPUT_TOPIC = env("OUTPUT_TOPIC")
    INPUT_ADDR = env("INPUT_ADDR")
    INPUT_TOPIC = env("INPUT_TOPIC")
    AUTHZ_SERVER_ADDR = env("AUTHZ_SERVER_ADDR")
    LOG_LEVEL = env("LOG_LEVEL")
    WAVE_PATH = env("WAVE_PATH")
    WAVE_FILES = env("WAVE_FILES")

    # Validate env address variable
    _validate_env_addr_variable(INPUT_ADDR, OUTPUT_ADDR, AUTHZ_SERVER_ADDR)
    # Validate env topic variable
    _validate_env_topic_variable(INPUT_TOPIC, OUTPUT_TOPIC)
    # Validate env log level variable
    _validate_env_log_level_variable(LOG_LEVEL)
    return (
        OUTPUT_ADDR,
        OUTPUT_TOPIC,
        INPUT_ADDR,
        INPUT_TOPIC,
        AUTHZ_SERVER_ADDR,
        LOG_LEVEL,
        WAVE_PATH,
        WAVE_FILES,
    )


def get_logger():
    import logging

    global LOG_LEVEL  # string
    level = logging.ERROR
    if LOG_LEVEL.upper() == "WARNING":
        level = logging.WARNING
    if LOG_LEVEL.upper() == "DEBUG":
        level = logging.DEBUG
    if LOG_LEVEL.upper() == "INFO":
        level = logging.INFO

    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)-20s ] - %(message)s",
        level=level,
    )
    logging.root.setLevel(level)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger


(
    OUTPUT_ADDR,
    OUTPUT_TOPIC,
    INPUT_ADDR,
    INPUT_TOPIC,
    AUTHZ_SERVER_ADDR,
    LOG_LEVEL,
    WAVE_PATH,
    WAVE_FILES,
) = _read_env_variables()
