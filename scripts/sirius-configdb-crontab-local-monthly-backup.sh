#!/bin/bash

source ~/.bashrc

BKP_FOLDER=$ROOT_GROUP/backups/configdb
REMOTE_PATH=$CONFIG_BACKUP_HOST/monthly

# Remove files older than 1 year
cd $BKP_FOLDER
find ./ -mtime +365 -type f -delete
# Copy new files to remote path
scp -rp *$(date "+%Y-%m-%d")*.tar.gz $REMOTE_PATH
