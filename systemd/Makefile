install-services:
	# mkdir -p /usr/local/etc/sirius-docker
	# cp ../docker-compose.yml /usr/local/etc/sirius-docker/sirius-docker-config-db.yml
	docker network create config-service
	cp -rf sirius-docker-config-db.service /etc/systemd/system
	cp -rf sirius-docker-config-db-mongo.service /etc/systemd/system
	cp -rf sirius-docker-config-db-api.service /etc/systemd/system
	systemctl enable sirius-docker-config-db.service sirius-docker-config-db-mongo.service sirius-docker-config-db-api.service
	systemctl daemon-reload

uninstall-services:
	# rm -rf /usr/local/etc/sirius-docker/sirius-docker-config-db.yml
	docker network rm config-service
	systemctl disable sirius-docker-config-db.service sirius-docker-config-db-mongo.service sirius-docker-config-db-api.service
	rm -rf /etc/systemd/system/sirius-docker-config-db.service
	rm -rf /etc/systemd/system/sirius-docker-config-db-mongo.service
	rm -rf /etc/systemd/system/sirius-docker-config-db-api.service
	systemctl daemon-reload
