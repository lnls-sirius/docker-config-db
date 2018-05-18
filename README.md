# Configuration database
The solution is composed of 2 services:
* the REST API server
* the database server

## Requirements
* docker
* docker-compose

## Development
* clone repository
* change to the repo folder
* production branch is *mongo*
* issue `docker-compose -f docker-compose-dev.yml up`
* the REST API server is exposed on port 80

## Deploy
* Install services in systemd
