#!/usr/bin/env python3
"""
 Copyright (C) 2021 Intel Corporation
 SPDX-License-Identifier: BSD-3-Clause
"""


from sanic import Sanic
from sanic import response
from sanic.log import logger
from rasa_wrapper import (
    authenticate,
    forward_to_rasa,
    update_secrets,
    get_sanic_server_ssl,
)


app = Sanic("nlp web server")
app = update_secrets(app)


@app.route("/webhooks/rest/webhook", methods=["POST"])
def on_post(req):
    try:
        if not authenticate(app, req):
            return response.json(None, status=403)
        return response.json(forward_to_rasa(app, req))

    except Exception as ex:
        import traceback

        logger.error(f"{traceback.format_exc()}")


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=False,
        access_log=False,
        ssl=get_sanic_server_ssl(app),
    )
