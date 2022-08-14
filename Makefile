.PHONY: build

setup: create-env init

create-env:
	python3 -m venv env

install:
	./env/bin/python3 -m pip install $(package)

uninstall:
	./env/bin/pip3 uninstall $(package)

lock:
	./env/bin/pip3 freeze > requirements.txt

list:
	./env/bin/pip3 list

init:
	./env/bin/pip3 install -r requirements.txt

test:
	./execute_test.sh 

docker-build:
	docker build -t personal-ledger:v1.0 --no-cache .

docker-run:
	docker run -v ${PWD}/volume:/app/volume --rm -d --name personal-ledger personal-ledger:v1.0

docker: docker-build docker-run

docker-stop:
	docker stop personal-ledger && docker rm personal-ledger
