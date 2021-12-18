#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from zmq_integration_lib import RPCServer, OutputPort, supported_cmds
from envparse import Env
import obp_helper
import getpass


SESSION_TIMEOUT_IN_SECS = 900


def _validate_env_addr_variable(OUTPUT_ADDR, SESSION_ADDR, TOKEN_SERVER_ADDR):
    for variable in [OUTPUT_ADDR, SESSION_ADDR, TOKEN_SERVER_ADDR]:
        if (
            not (type(variable) == str)
            or not (len(variable.split()) == 1)
            or not (("tcp" in variable.split(":")) or ("ipc" in variable.split(":")))
        ):
            raise ValueError("Please check {} address".format(variable))


def _validate_env_topic_variable(OUTPUT_TOPIC):
    if not (type(OUTPUT_TOPIC) == str) or not (len(OUTPUT_TOPIC.split()) == 1):
        raise ValueError("Please check {} topic".format(variable))


def _validate_env_log_level_variable(LOG_LEVEL):
    if not LOG_LEVEL.lower() in ["info", "error", "debug"] or not (
        len(LOG_LEVEL.split()) == 1
    ):
        raise ValueError("Please provide correct Log level")


def _variable_env_dev_variable(DEVELOPMENT):
    if not len(DEVELOPMENT.split()) == 1:
        raise ValueError("Please provide DEVELOPMENT variable value")


def _prepare_path_for_secret(secret):
    import os

    return os.path.join(os.path.join(os.path.join("/", "run"), "secrets"), secret)


def get_cert():
    cert = None
    if TLS_CERT is not None and TLS_KEY is not None:
        cert = tuple(map(_prepare_path_for_secret, (TLS_CERT, TLS_KEY)))
    return cert


def get_token_server():
    return RPCServer(TOKEN_SERVER_ADDR, supported_cmds)


def get_verfier_server():
    return RPCServer(SESSION_ADDR, supported_cmds)


def get_session_publish_port():
    return OutputPort(OUTPUT_ADDR, OUTPUT_TOPIC)


def session_publish(por, session_id, event):
    por.push(bytes(session_id, "utf-8"), event)


def logout(token):
    obp_helper.logout(token)


def display_help():
    print("The application needs the following environment variables.")
    print("INPUT_ADDR, INPUT_TOPIC, OUTPUT_ADDR, OUTPUT_TOPIC")
    print("Please set the variables and try again.")


def _get_login_token():
    print("Enter Credentials:")
    print("Enter Username:")
    dummy_input = input("Press any Key ")
    ask_for_input = input(
        "You would be prompted to enter credentials. Press any key to coninue"
    )
    user = input("username: ")
    password = getpass.getpass(prompt="password: ")
    apikey = getpass.getpass(prompt="apikey: ")
    token = obp_helper.get_login_token(user, password, apikey, cert=get_cert())
    if token == "":
        print("Login Failed")
    else:
        print("Login Successful")
    print("Press ctrl p Ctrl q to exit")
    return token


def _get_login_token_dev():
    enabled, user, passwd, apikey, token = _read_env_vars_development_only()
    if enabled and not token:
        token = obp_helper.get_login_token(user, passwd, apikey, cert=get_cert())
    if not enabled:
        return _get_login_token()
    return token


def get_login_token():
    if DEVELOPMENT:
        return _get_login_token_dev()
    else:
        return _get_login_token()


def _read_env_vars_development_only():

    env = Env(
        DEVELOPMENT=dict(cast=str, default="FALSE"),
        D_USERNAME=dict(cast=str, default="NONE"),
        D_PASS=dict(cast=str, default="NONE"),
        D_APIKEY=dict(cast=str, default="NONE"),
        D_TOKEN=dict(cast=str, default="NONE"),
    )
    DEVELOPMENT = env("DEVELOPMENT")
    D_USERNAME = env("D_USERNAME")
    D_PASS = env("D_PASS")
    D_APIKEY = env("D_APIKEY")
    D_TOKEN = env("D_TOKEN")
    # TODO: use lambda to replace 'NONE' with None in the return tuple
    if D_TOKEN == "NONE":
        D_TOKEN = None
    if DEVELOPMENT == "FALSE":
        return (False,)
    else:
        return (True, D_USERNAME, D_PASS, D_APIKEY, D_TOKEN)


def _read_env_variables():
    # Can set schema
    env = Env(
        OUTPUT_ADDR=str,
        OUTPUT_TOPIC=str,
        SESSION_ADDR=str,
        TOKEN_SERVER_ADDR=str,
        TLS_CERT=dict(cast=str, default="None"),
        TLS_KEY=dict(cast=str, default="None"),
        DEVELOPMENT=dict(cast=str, default="FALSE"),
        LOG_LEVEL=dict(cast=str, default="ERROR"),
    )

    TOKEN_SERVER_ADDR = env("TOKEN_SERVER_ADDR")
    OUTPUT_ADDR = env("OUTPUT_ADDR")
    OUTPUT_TOPIC = env("OUTPUT_TOPIC")
    LOG_LEVEL = env("LOG_LEVEL")
    SESSION_ADDR = env("SESSION_ADDR")
    DEVELOPMENT = env("DEVELOPMENT")
    TLS_CERT = env("TLS_CERT")
    TLS_KEY = env("TLS_KEY")
    if TLS_CERT is "None":
        TLS_CERT = None
    if TLS_KEY is "None":
        TLS_KEY = None
    if DEVELOPMENT == "FALSE":
        DEVELOPMENT = None
    # Validate env address variable
    _validate_env_addr_variable(OUTPUT_ADDR, SESSION_ADDR, TOKEN_SERVER_ADDR)
    # Validate env topic variable
    _validate_env_topic_variable(OUTPUT_TOPIC)
    # Validate env log level variable
    _validate_env_log_level_variable(LOG_LEVEL)
    return (
        OUTPUT_ADDR,
        OUTPUT_TOPIC,
        DEVELOPMENT,
        SESSION_ADDR,
        LOG_LEVEL,
        TOKEN_SERVER_ADDR,
        TLS_CERT,
        TLS_KEY,
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
        format="%(asctime)s - %(levelname)s  - [%(filename)s:%(lineno)s - %(funcName)-20s ] - %(message)s",
        level=level,
    )
    logging.root.setLevel(level)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger


(
    OUTPUT_ADDR,
    OUTPUT_TOPIC,
    DEVELOPMENT,
    SESSION_ADDR,
    LOG_LEVEL,
    TOKEN_SERVER_ADDR,
    TLS_CERT,
    TLS_KEY,
) = _read_env_variables()
