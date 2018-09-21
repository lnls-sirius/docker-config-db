#!/bin/bash

source ~/.bashrc

BKP_FOLDER=$ROOT_GROUP/backups/configdb
REMOTE_PATH=fernando-linux:$ROOT_GROUP/backups/configdb/daily

/usr/local/bin/sirius-configdb-backup.sh $BKP_FOLDER 'config-db' 'config-service'
# Remove files older than 30 days
cd $BKP_FOLDER
find ./ -mtime +30 -type f -delete
# Copy new files to remote path
scp -rp *$(date "+%Y-%m-%d")*.tar.gz $REMOTE_PATH
