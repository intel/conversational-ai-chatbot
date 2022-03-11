"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import os
from envparse import Env
from datetime import datetime, timedelta
from zmq_integration_lib import get_inpad, get_outpad
import jwt


def _prepare_path_for_secret(secret):
    import os

    return os.path.join(os.path.join(os.path.join("/", "run"), "secrets"), secret)


def get_cert():
    cert = None
    if TLS_CERT is not None and TLS_KEY is not None:
        cert = tuple(map(_prepare_path_for_secret, (TLS_CERT, TLS_KEY)))
    return cert


def get_cacert():
    # either return False or returns the path to a cacert
    cacert = False
    if TLS_CACERT:
        cacert = _prepare_path_for_secret(TLS_CACERT)
    return cacert


def get_inputport():
    ip = get_inpad(INPUT_ADDR, INPUT_TOPIC, AUTHZ_SERVER_ADDR)
    return ip


def get_outputport():
    op = get_outpad(OUTPUT_ADDR, OUTPUT_TOPIC)
    return op


def display_help():
    print("The application needs the following environment variables.")
    print("INPUT_ADDR, INPUT_TOPIC, OUTPUT_ADDR, OUTPUT_TOPIC")
    print("Please set the variables and try again.")


SERVER_URL = "https://rasa_action:8000"


def _read_docker_secret(secret_name):
    # docker secret path
    # build path to secret, read and return value of
    # secret file
    secret = None
    secret_file = os.path.join("/run/secrets", secret_name)
    # since file is opened using "with", no need to close explicitly
    with open(secret_file) as f:
        try:
            secret = f.read()
        except:
            if f.closed == False:
                f.close()
    return secret


def get_jwt():
    global JWT_SECRET
    jwt_secret = None
    try:
        jwt_secret = _read_docker_secret(JWT_SECRET)
    except FileNotFoundError:
        return ""

    JWT_ALGORITHM = "HS256"
    JWT_EXP_DELTA_SECONDS = 20

    payload = {
        "user": {"username": "user1", "role": "user"},
        "exp": datetime.utcnow() + timedelta(seconds=JWT_EXP_DELTA_SECONDS),
    }
    jwt_token = jwt.encode(payload, jwt_secret, JWT_ALGORITHM)

    # on linux decode is req, on windows not
    try:
        return jwt_token.decode("utf-8")
    except AttributeError:
        return jwt_token


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


def _validate_env_jwtsecret_variable(JWT_SECRET):
    if not len(JWT_SECRET.split()) == 1:
        raise ValueError("Please provide JWT_SECRET")


def _read_env_variables():
    # Can set schema
    env = Env(
        INPUT_ADDR=str,
        INPUT_TOPIC=str,
        OUTPUT_ADDR=str,
        OUTPUT_TOPIC=str,
        JWT_SECRET=str,
        AUTHZ_SERVER_ADDR=str,
        TLS_CERT=dict(cast=str, default="None"),
        TLS_KEY=dict(cast=str, default="None"),
        TLS_CACERT=dict(cast=str, default="None"),
        LOG_LEVEL=dict(cast=str, default="ERROR"),
    )

    INPUT_ADDR = env("INPUT_ADDR")
    INPUT_TOPIC = env("INPUT_TOPIC")
    OUTPUT_ADDR = env("OUTPUT_ADDR")
    OUTPUT_TOPIC = env("OUTPUT_TOPIC")
    AUTHZ_SERVER_ADDR = env("AUTHZ_SERVER_ADDR")
    JWT_SECRET = env("JWT_SECRET")
    LOG_LEVEL = env("LOG_LEVEL")
    TLS_CERT = env("TLS_CERT")
    TLS_KEY = env("TLS_KEY")
    TLS_CACERT = env("TLS_CACERT")
    if TLS_CERT is "None":
        TLS_CERT = None
    if TLS_KEY is "None":
        TLS_KEY = None
    if TLS_CACERT is "None":
        TLS_CACERT = None

    # Validate env address variable
    _validate_env_addr_variable(INPUT_ADDR, OUTPUT_ADDR, AUTHZ_SERVER_ADDR)
    # Validate env topic variable
    _validate_env_topic_variable(INPUT_TOPIC, OUTPUT_TOPIC)
    # Validate env log level variable
    _validate_env_log_level_variable(LOG_LEVEL)
    # Validate env JWT secrets variable
    _validate_env_jwtsecret_variable(JWT_SECRET)
    return (
        INPUT_ADDR,
        INPUT_TOPIC,
        OUTPUT_ADDR,
        OUTPUT_TOPIC,
        AUTHZ_SERVER_ADDR,
        JWT_SECRET,
        LOG_LEVEL,
        TLS_CERT,
        TLS_KEY,
        TLS_CACERT,
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
        # format="%(asctime)s - %(levelname)s - %(message)s", level=level)
        format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)s - %(funcName)-20s ] - %(message)s",
        level=level,
    )
    logging.root.setLevel(level)
    logger = logging.getLogger()
    logger.setLevel(level)
    return logger


(
    INPUT_ADDR,
    INPUT_TOPIC,
    OUTPUT_ADDR,
    OUTPUT_TOPIC,
    AUTHZ_SERVER_ADDR,
    JWT_SECRET,
    LOG_LEVEL,
    TLS_CERT,
    TLS_KEY,
    TLS_CACERT,
) = _read_env_variables()
