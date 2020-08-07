virtual: .venv/bin/pip 
.venv/bin/pip:
	virtualenv -p /usr/bin/python3 .venv
install:
	.venv/bin/pip install -Ur requirements.txt
update-requirements: install
	.venv/bin/pip freeze > requirements.txt
.PHONY: virtual install