#!/bin/bash
# Backup Sentry Tower Actual logs to GitHub

# ==== CONFIGURATION ====
LOG_FILES="/var/log/zabbix/zabbix_server.log"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LILROBOT="/home/ubuntu/lilrobot"

cd "$LILROBOT/logs" || exit 1
find . -type f -name "zabbix_server.log" -delete

cp $LOG_FILES .

sleep 1
git pull
sleep 2

if [[ -n $(git status --porcelain) ]]; then
    git add .
    git commit -m "Sentry Tower Actual - $TIMESTAMP"
    git push origin main
else
    echo "No changes detected. Skipping commit"
fi
# python3 "$LILROBOT/src/raspberrypi_server/status_indicator.py" --status "Backup Complete"
python3 "$LILROBOT/src/raspberrypi_server/oled_tester.py"

# ==== END CONFIGURATION ====
