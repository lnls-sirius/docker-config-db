#!/usr/bin/env bash
BKP_FILE=$1
BKP_FOLDER=$(echo $BKP_FILE | sed 's/\..*//')
CONTAINER_NAME="config-db"
NETWORK="config-service"
WRK_DIR=/tmp/$CONTAINER_NAME
BKP_DIR=$ROOT_GROUP/backups/configdb"

mkdir -p $WRK_DIR
tar -C $WRK_DIR -xvf $BKP_DIR/$1
chmod -R +777 $BKP_DIR
sudo docker run --rm --network $NETWORK --link $CONTAINER_NAME:mongo -v $WRK_DIR/$BKP_FOLDER:/backup mongo mongorestore --drop -v --host $CONTAINER_NAME /backup
rm -rf $WRK_DIR
