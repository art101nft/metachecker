# metachecker
Preview and collaborate on your NFT project metadata before going live

## Setup

Tools you will need:
* Docker  # apt-get install docker.io
* docker-compose  # apt-get install docker-compose
* python3 (linux os will have this)
* python3-venv  # apt-get install python3-venv

### Development

I have provided a `Makefile` with some helpful stuff...make sure to install `make` to use it.

```
# install python virtual environment and install application dependencies
make setup

# setup secrets
cp env-example .env && vim .env

# run services (ipfs + redis cache)
make up

# initialize sqlite database w/ schema via alembic
make init

# run huey
make huey

# run development server
make dev

# access at http://127.0.0.1:5000
```
