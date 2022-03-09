"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


import json
import os
import requests
import jwt


SERVER_URL = "http://localhost:5005"


def get_sanic_server_ssl(app):
    # read sanic variables
    ssl = {
        "cert": os.path.join("/run/secrets", app.config.SERVERCERT),
        "key": os.path.join("/run/secrets", app.config.SERVERKEY),
    }
    return ssl


def get_client_cert(app):
    return (
        os.path.join("/run/secrets", app.config.TLS_CERT),
        os.path.join("/run/secrets", app.config.TLS_KEY),
    )


def update_secrets(app):
    # read env vars
    # SANIC_JWTSECRET
    # SANIC_JWTALGORITHM
    jwt_secret = None
    jwt_algorithm = None
    try:
        jwt_secret = _read_docker_secret(app.config.JWTSECRET)
        jwt_algorithm = _read_docker_secret(app.config.JWTALGORITHM)
    except Exception as msg:
        print("authenticate failed: ", msg)
    app.config["jwt_secret"] = jwt_secret
    app.config["jwt_algorithm"] = jwt_algorithm
    return app


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


def authenticate(app, req):
    jwt_token = req.token
    try:
        jwt_secret = app.config.jwt_secret
        jwt_algorithm = app.config.jwt_algorithm
    except Exception as msg:
        print("authenticate failed: ", msg)
        return False
    return _verify_token(jwt_token, jwt_secret, jwt_algorithm)


def _verify_token(jwt_token, JWT_SECRET, JWT_ALGORITHM):
    ret = False
    try:
        _ = json.loads(json.dumps(jwt.decode(
            jwt_token, JWT_SECRET, JWT_ALGORITHM)))
        ret = True
    except Exception as msg:
        print("Token failed ", msg)
    return ret


def forward_to_rasa(app, req):
    # connect to rasa and send
    print(req.json)
    # TODO: remove setting proxies to somewhere else
    os.environ["http_proxy"] = ""
    os.environ["https_proxy"] = ""
    # curl localhost:5005/webhooks/rest/webhook -d '{"sender": "user1", "message":"show atms for Pune Bank"}'
    # validate req
    data = req.json
    # validate data

    payload = {"sender": data["sender"], "message": data["message"]}
    headers = {"content-type": "application/json"}
    # r = requests.post(SERVER_URL + '/webhooks/rest/webhook', headers=headers, data = json.dumps(payload), verify=False,cert = get_client_cert(app) )
    r = requests.post(
        SERVER_URL + "/webhooks/rest/webhook", headers=headers, data=json.dumps(payload)
    )
    return r.json()
