setup: 
	# Preparing virtual environment to installing core dependencies
	python -m pip install pipenv &&\
	pipenv --python 3.8 &&\
	pipenv shell &&\
	python -m pip install --upgrade pip

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
	
lint: install
	# Scanning dockerfile
	sudo ./hadolint --ignore DL3003 --ignore DL3018 ./Dockerfile
	# Scanning source code
	black ./
	pylint --ignore=migrations,settings.py,manage.py -d W ./*.py

migrations: 
	flask db init --multidb
	flask db stamp head
	flask db migrate
	flask db upgrade

test:
	# Running test with converage
	coverage run -m py.test -vv &&\
    coverage report -m --fail-under=70 &&\
	rm -f ./hadolint


all: install lint test
