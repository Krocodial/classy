#!/bin/bash

python /opt/app-root/src/manage.py migrate
python /opt/app-root/src/manage.py createcachetable
