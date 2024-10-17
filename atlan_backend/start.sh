#!/bin/bash

service nginx start

gunicorn atlan_backend.asgi:application -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000