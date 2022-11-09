all: install env_setting

install:
	sudo apt-get update
	sudo apt-get -y upgrade
	sudo apt-get install -y python3 python3-pip git build-essential libcap-dev
	sudo apt-get install -y sysfsutils cgroup-tools
	sudo mkdir ~/isolate
		sudo git clone https://github.com/ioi/isolate.git ~/isolate
	sudo make -C ~/isolate isolate
	sudo make -C ~/isolate install
	sudo mkdir /etc/nuoj-sandbox
	sudo git clone --recursive https://github.com/ntut-xuan/NuOJ-Sandbox.git /etc/nuoj-sandbox
	sudo mkdir /etc/nuoj-sandbox/storage
	sudo mkdir /etc/nuoj-sandbox/storage/testcase
	sudo mkdir /etc/nuoj-sandbox/storage/submission
	sudo mkdir /etc/nuoj-sandbox/storage/result
	sudo chmod -R 647 /etc/nuoj-sandbox/*
	sudo cp /etc/nuoj-sandbox/nuoj-sandbox.service /etc/systemd/system/
	sudo chmod 647 /etc/systemd/system/nuoj-sandbox.service
	sudo pip3 install flask
	sudo systemctl daemon-reload
	sudo systemctl enable nuoj-sandbox
	sudo systemctl start nuoj-sandbox
	

env_setting:
	sudo python3 /etc/nuoj-sandbox/env_setting.py ${reboot}
