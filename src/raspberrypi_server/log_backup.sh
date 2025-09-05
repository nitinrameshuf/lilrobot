#!/bin/bash
# Backup Sentry Tower Robot  logs to GitHub

# ==== CONFIGURATION ====
SRC_DIR="$LILROBOT/src"  
LOG_FILES="/var/log/zabbix/zabbix_server.log /var/log/zabbix/zabbix_agentd.log"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

cd

git add .
git commit -m "Routine Log Backup"
git push origin main

python3 
