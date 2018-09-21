#!/usr/bin/env bash

if [[ $# -ne 3 ]]; then
	echo 'Usage: backup_file container_name container_network'
	echo ''

	echo 'Containers:'
	echo $(docker container ls --format "{{.Names}}")
	echo ''

	echo 'Networks:'
	echo $(docker network ls --format "{{.Name}}")
	echo ''
	
	exit 1
fi

BKP_FILE=$1
CONTAINER_NAME=$2
NETWORK=$3

BKP_FOLDER=$(basename $BKP_FILE | sed 's/\..*//')
WRK_DIR=/tmp/$CONTAINER_NAME

mkdir -p $WRK_DIR
tar -C $WRK_DIR -xvf $BKP_FILE
chmod -R +777 $BKP_FILE
sudo docker run --rm --network $NETWORK --link $CONTAINER_NAME:mongo -v $WRK_DIR/tmp/$BKP_FOLDER:/backup mongo mongorestore --drop -v --host $CONTAINER_NAME /backup
rm -rf $WRK_DIR

exit 0

