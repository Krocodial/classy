#!/bin/bash

python /home/classy/manage.py migrate
python /home/classy/manage.py createcachetable
