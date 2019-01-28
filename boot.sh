#!/bin/sh
source venv/bin/activate
nohup venv/bin/flask run -p 5000 -h 0.0.0.0
