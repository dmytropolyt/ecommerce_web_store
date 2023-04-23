#!/usr/bin/env bash

echo "[Unit]
Name=Celery
Description=Celery service for app
After=network.target
StartLimitInterval=0
[Service]
Type=simple
Restart=always
RestartSec=30
User=root
WorkingDirectory=/var/app/current
ExecStart=$PYTHONPATH/celery -A app worker --loglevel=INFO
ExecReload=$PYTHONPATH/celery -A app worker --loglevel=INFO
EnvironmentFile=/opt/elasticbeanstalk/deployment/env
[Install]
WantedBy=multi-user.target
" | tee /etc/systemd/system/celery.service

# Start celery service
systmectl statr celery.service

# Enable celery service to load on system start
systmectl enable celery.service