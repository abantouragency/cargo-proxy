# -*- coding: utf-8 -*-
"""Proxy service: forwards all requests to the healthy Render IP (216.24.57.15)."""

import os, sys
from flask import Flask, request, Response
import requests as rq

TARGET = "http://216.24.57.15"

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
def proxy(path):
    url = f"{TARGET}/{path}"
    if request.query_string:
        url += "?" + request.query_string.decode("utf-8")
    
    # Forward the request
    headers = {k: v for k, v in request.headers if k.lower() not in ("host", "content-length", "transfer-encoding", "connection")}
    
    try:
        resp = rq.request(
            method=request.method,
            url=url,
            headers=headers,
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            timeout=30
        )
        excluded = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        resp_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded]
        return Response(resp.content, status=resp.status_code, headers=resp_headers)
    except rq.exceptions.RequestException as e:
        return Response(f"Proxy error: {e}", status=502)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)