#!/usr/bin/env bash
export SETTINGS=../config.cfg
export FLASK_ENV=development
export FLASK_APP=flaskr/__init__.py
flask run --host=0.0.0.0 # for external visibility of the server