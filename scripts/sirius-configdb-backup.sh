#!/usr/bin/env bash

if [[ $# -ne 3 ]]; then
	echo 'Usage: backup_folder container_name container_network'
	echo ''

	echo 'Containers:'
	echo $(docker container ls --format "{{.Names}}")
	echo ''

	echo 'Networks:'
	echo $(docker network ls --format "{{.Name}}")
	echo ''
	
	exit 1
fi

BKP_DIR=$1
CONTAINER_NAME=$2
NETWORK=$3

WRK_DIR=/tmp

function backup_databases {
    RUNNING=$(docker ps | grep $CONTAINER_NAME)
    if [ ! -z "${RUNNING}" ]; then
	      printf "backing config-db ...\n"
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
        printf "Container config-db not running\n"
    fi
}

backup_databases
