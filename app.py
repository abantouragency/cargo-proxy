# -*- coding: utf-8 -*-
"""Proxy service: forwards all requests to the healthy cargo-abantour service.
Forces the Host header so Render routes to the correct app."""

import os
from flask import Flask, request, Response
import requests as rq

TARGET_HOST = os.environ.get("TARGET_HOST", "cargo-abantour.onrender.com")
TARGET = os.environ.get("TARGET_URL", f"https://{TARGET_HOST}")

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}"
    if request.query_string:
        url += "?" + request.query_string.decode("utf-8")

    # Force Host header to the target site so Render routes correctly,
    # and drop hop-by-hop headers.
    headers = {k: v for k, v in request.headers.items()
               if k.lower() not in ("host", "content-length", "transfer-encoding", "connection", "accept-encoding")}
    headers["Host"] = TARGET_HOST

    try:
        resp = rq.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=True,
            timeout=30,
            verify=True
        )
        excluded = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        resp_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]
        return Response(resp.content, status=resp.status_code, headers=resp_headers)
    except rq.exceptions.RequestException as e:
        return Response(f"Proxy error: {e}", status=502)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)