#!/usr/bin/env bash

BKP_DIR=$ROOT_GROUP/backups/configdb
WRK_DIR=/tmp
CONTAINER_NAME="configdb_config-db_1"
NETWORK="configdb_default"

function backup_databases {
    RUNNING=$(docker ps | grep $CONTAINER_NAME)
    if [ ! -z "${RUNNING}" ]; then
	      printf "backing dockerconfigdb_config-db_1 up ...\n"
        fname=dump_config_db_`date +%Y-%m-%d"_"%H-%M-%S`
	# Allow docker to write backup to folder
        mkdir -m 777 $WRK_DIR/$fname/
	# Give permission to write on newly created files of the docker group
	setfacl -d -m group:docker:rwx $WRK_DIR/$fname
	# Run docker to dump db
        docker run --rm --network $NETWORK --link $CONTAINER_NAME:mongo -v $WRK_DIR/$fname:/backup mongo mongodump --out=/backup --host=$CONTAINER_NAME
	# Extract to backup folder and remove files on /tmp
        tar zcvf $BKP_DIR/$fname.tar.gz $WRK_DIR/$fname
        rm -rf $WRK_DIR/$fname
    else
        printf "service docker_config-db_1 not running\n"
    fi
}

backup_databases
