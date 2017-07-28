FROM mysql

ENV MYSQL_DATABASE=sirius
ENV MYSQL_ROOT_PASSWORD=root

COPY configuration.sql /docker-entrypoint-initdb.d

EXPOSE 3306
