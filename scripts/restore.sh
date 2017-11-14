#!/usr/bin/env bash
BKP_FILE=$1
CONTAINER_NAME="docker_config-db_1"
NETWORK="docker_default"
WRK_DIR="/home/fac_files/lnls-sirius/docker-config-db/backups"
BKP_DIR="/home/fac_files/lnls-sirius/docker-config-db/backups"

mkdir $WRK_DIR/tmp
tar -C $WRK_DIR/tmp -xvf $BKP_DIR/$1
chmod -R +777 $BKP_DIR/tmp/backup
sudo docker run --rm --network $NETWORK --link $CONTAINER_NAME:mongo -v $WRK_DIR/tmp/backup:/backup mongo mongorestore --drop -v --host $CONTAINER_NAME /backup
rm -rf $WRK_DIR/tmp
