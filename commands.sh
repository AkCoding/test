#!/usr/bin/env bash
cd /home/ec2-user/NLP_API

echo '[INSTALL] Using latest pip'
pip3 install --upgrade pip wheel

echo '[INSTALL] Installing Requirements'
pip3 install -r requirements.txt

echo '[RUNNNING] MIGRATIONS'
python3 run_migrations.py

echo '[STOP] SppechToTextJobber'
pm2 stop SppechToTextJobber

echo '[STOP] TranscribeAPI'
pm2 stop TranscribeAPI

echo '[START] TranscribeAPI'
pm2 start ecosystem.config.json






