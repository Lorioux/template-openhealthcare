setup: 
	# Preparing virtual environment to installing core dependencies
	python -m pip install --upgrade pip  &&\
	pip install pipenv &&\
	if [ -e "./.venv" ]; then echo "Exist .venv"; else mkdir .venv; fi; 
	pipenv --python 3.8 &&\
	pipenv run pip install --upgrade pip

install: setup
	# Updating package installer
	# Installing dependecies
	pipenv install --dev --skip-lock
	# install hadolint in not exists
	if [ -e "./hadolint" ]; then \
		echo "Found hadolint in this directory." ; \
	else \
		sudo wget -O hadolint https://github.com/hadolint/hadolint/releases/download/v1.16.3/hadolint-Linux-x86_64 &&\
		sudo chmod +x hadolint; \
	fi
	# install postgres dependency
	sudo apt install python3-psycopg2
	
lint: 
	# Scanning dockerfile
	sudo ./hadolint --ignore DL3003 --ignore DL3018 ./Dockerfile
	# Scanning source code
	pipenv run black ./
	pipenv run pylint --ignore=migrations,settings.py,manage.py -d W ./openhcs/*.py

migrations: 
	pipenv run flask db init --multidb
	pipenv run flask db stamp head
	pipenv run flask db migrate
	pipenv run flask db upgrade

test: 
	# Running test with converage
	pipenv run coverage run -m py.test -vv &&\
    pipenv run coverage report -m --fail-under=70 &&\
	rm -f ./hadolint


all: install lint test
