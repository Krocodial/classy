#!/bin/bash

python /opt/app-root/manage.py migrate
python /opt/app-root/manage.py createcachetable
