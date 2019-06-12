docker-compose -f docker-compose-dev.yml up --force-recreate --build
## execute command below in another terminal to restore some mongo image
## to the empty fresh DB initialized by the command above:
# sirius-configdb-restore.sh \
#    /home/fernando/Desktop/dump_config_db_2019-04-12_17-29-45.tar.gz \
#    dockerconfigdb_config-db_1 dockerconfigdb_default
