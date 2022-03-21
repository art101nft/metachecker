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

# --------------------------------------------------------------------------------
#                       STEP-BY-STEP DEVELOPMENT SET-UP
# --------------------------------------------------------------------------------

# (1) - Install Python Virtual Environment / Application dependencies
make setup

# (2) - Setup config secrets. NOTE: DATA_FOLDER should point to a real directory.
cp env-example .env && vim .env

# (3) - Start your Python Virtual Environment
source .venv/bin/activate

# (4) Install Huey and Redis via pip3
pip3 install huey
pip3 install redis

# (5) Run IPFS / Redis Cache Services
make up

# (6) Initialize SQLite Database w/ Schema via Alembic
make init

# (7) Run Huey
make huey

# (8) In a new Terminal window, Run development server
make dev

# (9) Access the server at http://127.0.0.1:5000. (Make sure SERVER_NAME matches current server name)
```
