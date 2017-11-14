#!/usr/bin/env bash
WRK_DIR="/tmp"
BKP_DIR="/home/fac_files/lnls-sirius/docker-config-db/backups"
CONTAINER_NAME="docker_config-db_1"
NETWORK="docker_default"
function backup_databases {
    RUNNING=$(sudo docker ps | grep docker_config-db_1)
    if [ ! -z "${RUNNING}" ]; then
	      printf "backing dockerconfigdb_config-db_1 up ...\n"
        fname=dump_config_db_`date +%Y-%m-%d"_"%H-%M-%S`
        mkdir -p $WRK_DIR/backup
        chmod +777 $WRK_DIR/backup/
        docker run --rm --network $NETWORK --link $CONTAINER_NAME:mongo -v $WRK_DIR/backup:/backup mongo mongodump --out=/backup --host=$CONTAINER_NAME
        tar zcvf $BKP_DIR/$fname.tar.gz $WRK_DIR/backup/
        rm -rf $WRK_DIR/backup
    else
        printf "service docker_config-db_1 not running\n"
    fi
}

backup_databases
