"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""

from obp_api import base
import os
import logging as log
import requests

requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning
)


def _login(configfile, cert):
    connection_helper = base.Connector(configfile, cert)
    connection_helper.login()
    return connection_helper


def logout(token):
    pass


def _prepare_login_config(user, pwd, apikey):
    import io
    import yaml

    yaml_str = """credentials:
  URL: https://apisandbox.openbankproject.com
  API: v4.0.0
  username:
  password:
  consumer_key:
    """
    data = yaml.safe_load(yaml_str)
    # data['credentials']['URL'] = BASE_URL
    data["credentials"]["username"] = user
    data["credentials"]["password"] = pwd
    data["credentials"]["consumer_key"] = apikey
    configyam = io.StringIO()
    yaml.dump(data, configyam)
    return io.StringIO(configyam.getvalue())


def get_login_token(user, pwd, apikey, cert=None):
    connector = _login(_prepare_login_config(user, pwd, apikey), cert)
    return connector.TOKEN
