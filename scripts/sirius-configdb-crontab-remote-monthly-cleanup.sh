#!/bin/bash

source ~/.bashrc

BKUP_PATH=$ROOT_GROUP/backups/configdb/monthly

if [ -d $BKUP_PATH ]; then
	cd $BKUP_PATH
	find ./ -mtime +365 -type f -delete
fi
