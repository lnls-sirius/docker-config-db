INSTALL_DIR=/usr/local/bin

install:
	cp -f scripts/* $(INSTALL_DIR)/
	$(MAKE) -C systemd

develop:
	sudo ln -fs $(PWD)/scripts/* $(INTALL_DIR)/
	sudo $(MAKE) -C systemd
