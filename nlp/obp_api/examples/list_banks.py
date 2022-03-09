#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

import os
from obp_api import atm, banks, accounts
from obp_api import base
from argparse import ArgumentParser, SUPPRESS
import logging as log


def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group("Options")
    args.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="Show this help message and exit.",
    )
    args.add_argument("-c", "--config", help="Config file.",
                      required=True, type=str)
    return parser


def backend_helper(config_file):
    connection_helper = base.Connector(config_file)
    connection_helper.login()
    return connection_helper


def main():
    args = build_argparser().parse_args()
    config_file = args.config
    conn = backend_helper(config_file)
    bank_ = banks.Bank(conn)
    list_of_banks = bank_.get_banks()
    try:
        def names(x): return "  {0}".format(x["full_name"])
        banknames = map(names, list_of_banks)
        texti = "\n".join(list(banknames))
    except Exception:
        texti = "Could not get bank list"

    #print(texti)


if __name__ == "__main__":
    main()
