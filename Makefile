setup:
	python3 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	mkdir -p data/json

shell:
	bash manage.sh shell

init:
	.venv/bin/alembic upgrade head

dev:
	bash manage.sh run

prod:
	bash manage.sh prod

up:
	docker-compose up -d

huey:
	.venv/bin/huey_consumer metachecker.tasks.huey -w 1

install-ipfs:
	wget https://dist.ipfs.io/go-ipfs/v0.10.0/go-ipfs_v0.10.0_linux-amd64.tar.gz
	tar -xvzf go-ipfs_v0.10.0_linux-amd64.tar.gz
	cd go-ipfs && bash install.sh

run-ipfs:
	ipfs daemon

kill:
	pkill -e -f metachecker
