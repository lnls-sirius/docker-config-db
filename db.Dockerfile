FROM mongo:3.6

COPY db_configuration.js /docker-entrypoint-initdb.d

EXPOSE 27017
