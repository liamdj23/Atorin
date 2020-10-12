dependencies:
	wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
	echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
	sudo curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
	echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
	sudo apt update
	sudo apt install -y mongodb-org influxdb
	sudo systemctl daemon-reload
	sudo systemctl start influxdb
	sudo systemctl start mongod
config:
	cd src && python3 settings/__init__.py
python-dependencies:
	python3 -m pip install --user virtualenv
virtual: .venv/bin/pip
.venv/bin/pip:
	virtualenv -p python3 .venv
install:
	.venv/bin/pip install -Ur requirements.txt
update-requirements: install
	.venv/bin/pip freeze > requirements.txt
.PHONY: dependencies python-dependencies virtual install config