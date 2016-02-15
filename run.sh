#!/usr/bin/env bash
mongod -dbpath ./database/ --port 22222 &
# python3 ./server.py --port=8000 --dbport=11111 &
python3 ./server.py --port=8888 --dbport=22222 --logging=debug