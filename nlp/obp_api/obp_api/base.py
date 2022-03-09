"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import json
import requests as rq
import yaml
import io


def write_config(data, config_file):
    if not type(config_file) == (io.StringIO or io.BytesIO):
        context_mgr = open(config_file, "w")
        # since file is opened using "with", no need to close explicitly
        with context_mgr as f:
            try:
                data = yaml.dump(data, f)
            except:
                if f.closed == False:
                    f.close()


# Support StringIO and fileIO
def load_config(CONFIGFILE):
    if type(CONFIGFILE) == (io.StringIO or io.BytesIO):
        context_mgr = CONFIGFILE
    else:
        context_mgr = open(CONFIGFILE, "w")

    # since file is opened using "with", no need to close explicitly
    with context_mgr as f:
        try:
            # data = yaml.load(f, Loader = yaml.FullLoader)
            data = yaml.safe_load(f)
        except:
            if f.closed == False:
                f.close()
    try:
        global BASE_URL, API_VERSION
        BASE_URL = data["credentials"]["URL"]
        API_VERSION = data["credentials"]["API"]
        return data
    except (KeyError, IndexError):
        print("yaml doesn't have key credentials")
        return {}


class apiObject(object):
    def __init__(self, connector, api_version="v4.0.0"):
        self.connector = connector
        self.api_version = api_version

    def request(self, cmd, endpoint, data=""):
        return self.connector.request(cmd, endpoint, data)


class Connector(object):
    BASE_URL = ""
    TOKEN = ""

    def __init__(self, config_file="config.yml", cert=None):
        # cert = (cert_file_path, key_file_path) # certs should be provided like this
        self.config = config_file
        self.cert = cert

    def login(self):
        endpoint = "/my/logins/direct"
        data = load_config(self.config)
        creds = data["credentials"]
        # Set base url
        self.BASE_URL = creds["URL"]
        print(self.BASE_URL)
        try:
            self.TOKEN = creds["TOKEN"]
        except (KeyError, IndexError):
            url = self.BASE_URL + endpoint
            # print ("URL: {}".format(url))
            # payload = {'some': 'data'}
            headers = {"Content-Type": "application/json"}
            auth = "DirectLogin username=%s,password=%s,consumer_key=%s" % (
                creds["username"],
                creds["password"],
                creds["consumer_key"],
            )
            headers["Authorization"] = auth

            r = rq.post(url, headers=headers, verify=False)
            if "token" in r.json():
                try:
                    self.TOKEN = r.json()["token"]
                    data["credentials"]["TOKEN"] = self.TOKEN
                    write_config(data, self.config)
                except Exception as msg:
                    print("Could not obtain token", msg)
            else:
                print("Could not obtain token")

    def get_request_headers(self):
        h = {
            "Content-Type": "application/json",
            "Authorization": "DirectLogin token=%s" % self.TOKEN,
        }
        return h

    def refresh_token(self):
        pass

    def request(self, cmd, endpoint, data=""):
        if "get" == cmd:
            url = "{0}{1}".format(self.BASE_URL, endpoint)
            h = self.get_request_headers()
            # print ("Connector: GET: on ", url)
            if self.cert is not None:
                return rq.get(url, headers=h, cert=self.cert)
            return rq.get(url, headers=h)
        if "post" == cmd:
            if self.cert is not None:
                return rq.post(
                    url, json=data, headers=get_request_headers(), cert=self.cert
                )
            return rq.post(url, json=data, headers=get_request_headers())
