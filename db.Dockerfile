FROM mysql

COPY db_configuration.sql /docker-entrypoint-initdb.d

EXPOSE 3306
