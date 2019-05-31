INSTALL_DIR=/usr/local/bin

install:
	sudo cp -f scripts/* $(INSTALL_DIR)/
	sudo $(MAKE) -C systemd

develop:
	sudo ln -fs $(pwd)/scripts/* $(INSTALL_DIR)/
	sudo $(MAKE) -C systemd
