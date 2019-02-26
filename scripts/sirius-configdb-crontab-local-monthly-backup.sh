#!/bin/bash

source ~/.bashrc

BKP_FOLDER=$ROOT_GROUP/backups/configdb
REMOTE_PATH=$ROOT_GROUP/backups/backups-lnls452/monthly

# Remove files older than 1 year
cd $BKP_FOLDER
find ./ -mtime +365 -type f -delete
# Copy new files to remote path
cp *$(date "+%Y-%m-%d")*.tar.gz $REMOTE_PATH
