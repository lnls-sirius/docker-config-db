#!/bin/bash

source ~/.bashrc

BKP_FOLDER=$ROOT_GROUP/backups/configdb
REMOTE_PATH=$ROOT_GROUP/backups/backups-lnls452/daily

/usr/local/bin/sirius-configdb-backup.sh $BKP_FOLDER 'config-db' 'config-service'
# Remove files older than 30 days
cd $BKP_FOLDER
find ./ -mtime +30 -type f -delete
# Copy new files to remote path
cp *$(date "+%Y-%m-%d")*.tar.gz $REMOTE_PATH
