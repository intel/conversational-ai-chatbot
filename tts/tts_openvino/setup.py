"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from setuptools import setup

setup(
    name="tts_openvino",
    version="0.0.1",
    install_requires=[
        "numpy",
        "inflect",
        "scipy==1.5.4",
    ],
    packages=["tts_openvino", "tts_openvino/models", "tts_openvino/utils"],
)
