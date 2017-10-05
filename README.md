# Configuration database
The solution is composed of 2 services:
* the REST API server
* the database server

## Requirements
* docker
* docker-compose

## How to use
* clone repository
* make sure to meet the requirements
* change to the repo folder
* issue `docker-compose up`
* the REST API server is exposed on port 80

## Virtual Environment (local development)
For local development a virtual env can be created in which the requirements are installed:
* `python -m venv ./{NEW_DIR}`
* `source ./{NEW_DIR}/bin/activate`
* `pip install requirements.txt`
