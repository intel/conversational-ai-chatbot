"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import re
import logging


def find(line, variable):
    try:
        value = str.split(
            re.sub("[^-_/.A-Za-z0-9]+", " ", line.rstrip("\n")), " "
        ).index(variable)
        value = str.split(re.sub("[^-_/.A-Za-z0-9]+", " ", line.rstrip("\n")), " ")[
            value + 1
        ]
        info = "found value of " + variable + "=" + value
        logging.debug(f"found value of {variable} = {value}")
        return value
    except ValueError:
        return False


def parser(variable, data):
    for line in data:
        value = find(line, variable)
        if value == False:
            continue
        else:
            return value


# TODO: Change parser to read from file once and keep the data in a dict.
def parse_config(asr_config):
    # parse config and take out info

    # since file is opened using "with", no need to close explicitly
    with open(asr_config, "r") as f:
        try:
            data = f.readlines()
            model_bin = parser("model_bin", data)
            model_xml = parser("model_xml", data)
            device = parser("device", data)
            alphabet_cfg = parser("alphabet_config", data)
            version = parser("version", data)
            sample_rate = 16000
            lm = parser("lm", data)
        except Exception as msg:
            if f.closed == False:
                f.close()
            logging.error("received Exception: {}".format(msg))
    return (model_xml, model_bin, device, alphabet_cfg, sample_rate, version, lm)
