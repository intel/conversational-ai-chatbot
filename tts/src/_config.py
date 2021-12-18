"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from envparse import Env
from zmq_integration_lib import get_inpad, get_outpad


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


def _validate_env_play_audio_variable(PLAY_AUDIO):
    if not type(PLAY_AUDIO) == bool:
        raise ValueError("Please check PLAY_AUDIO value ")


duration_model = "/model/text-to-speech-en-0001-duration-prediction.xml"
regression_model = "/model/text-to-speech-en-0001-regression.xml"
generation_model = "/model/text-to-speech-en-0001-generation.xml"


def _read_env_variables():
    # Can set schema
    env = Env(
        INPUT_ADDR=str,
        INPUT_TOPIC=str,
        OUTPUT_ADDR=str,
        OUTPUT_TOPIC=str,
        AUTHZ_SERVER_ADDR=str,
        PLAY_AUDIO=dict(cast=str, default="None"),
        LOG_LEVEL=dict(cast=str, default="ERROR"),
    )

    INPUT_ADDR = env("INPUT_ADDR")
    INPUT_TOPIC = env("INPUT_TOPIC")
    OUTPUT_ADDR = env("OUTPUT_ADDR")
    OUTPUT_TOPIC = env("OUTPUT_TOPIC")
    AUTHZ_SERVER_ADDR = env("AUTHZ_SERVER_ADDR")
    PLAY_AUDIO = env("PLAY_AUDIO")
    if PLAY_AUDIO == "None":
        PLAY_AUDIO = False
    else:
        PLAY_AUDIO = True
    LOG_LEVEL = env("LOG_LEVEL")

    # Validate env address variable
    _validate_env_addr_variable(INPUT_ADDR, OUTPUT_ADDR, AUTHZ_SERVER_ADDR)

    # Validate env topic variable
    _validate_env_topic_variable(INPUT_TOPIC, OUTPUT_TOPIC)

    # Validate env log level variable
    _validate_env_log_level_variable(LOG_LEVEL)

    # Validate env Play audio variable
    _validate_env_play_audio_variable(PLAY_AUDIO)

    return (
        INPUT_ADDR,
        INPUT_TOPIC,
        OUTPUT_ADDR,
        OUTPUT_TOPIC,
        AUTHZ_SERVER_ADDR,
        PLAY_AUDIO,
        LOG_LEVEL,
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
    INPUT_ADDR,
    INPUT_TOPIC,
    OUTPUT_ADDR,
    OUTPUT_TOPIC,
    AUTHZ_SERVER_ADDR,
    PLAY_AUDIO,
    LOG_LEVEL,
) = _read_env_variables()


def play_audio(wave_data):
    import simpleaudio as sa

    wave_obj = sa.WaveObject(wave_data, 1, 2, 16000)
    play = wave_obj.play()
    play.wait_done()
