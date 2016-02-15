#!/usr/bin/bash
export LC_ALL=C
mongod -dbpath ./database/ --port 12321 &
python3 ./server.py --port=8000 --dbport=12321 &
python3 ./server.py --port=8001 --dbport=12321 &
python3 ./server.py --port=8002 --dbport=12321 &
python3 ./server.py --port=8003 --dbport=12321 &
sudo nginx -c `pwd`/nginx.conf