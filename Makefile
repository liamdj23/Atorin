dependencies:
	python3 -m pip install --user virtualenv
virtual: .venv/bin/pip
.venv/bin/pip:
	virtualenv -p python3 .venv
install:
	.venv/bin/pip install -Ur requirements.txt
update-requirements: install
	.venv/bin/pip freeze > requirements.txt
.PHONY: dependencies virtual install