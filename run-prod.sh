#!/usr/bin/env bash
export SETTINGS=../config.cfg
export FLASK_ENV=production
export FLASK_APP=flaskr/__init__.py

nohup waitress-serve --no-expose-tracebacks --call 'flaskr:get_app_instance' &