"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from setuptools import setup

setup(
    name="obp_api",
    version="0.0.1",
    install_requires=[
        "requests",
        "pyyaml",
    ],
    packages=["obp_api"],
)
