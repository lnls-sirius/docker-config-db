FROM mongo

COPY db_configuration.js /docker-entrypoint-initdb.d

EXPOSE 27017
