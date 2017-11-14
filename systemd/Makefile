install-services:
	mkdir -p /usr/local/bin/docker
	cp ../docker-compose.yml /usr/local/bin/docker/sirius-docker-config-db.yml
	cp -rf sirius-docker-config-db.service /etc/systemd/system
	systemctl enable sirius-docker-config-db.service
	systemctl daemon-reload

uninstall-services:
	rm -rf /usr/local/bin/docker/sirius-docker-config-db.yml
	systemctl disable sirius-docker-config-db.service
	rm -rf /etc/systemd/system/sirius-docker-config-db.service
	systemctl daemon-reload
