"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from setuptools import setup

setup(
    name="asr",
    version="1.0",
    install_requires=[
        "deepspeech_openvino",
    ],
    packages=["asr"],
)
