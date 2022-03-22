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

# (3) Run IPFS / Redis Cache Services
make up

# (4) Initialize SQLite Database w/ Schema via Alembic
make init

# (5) Run Huey
make huey

# (6) In a new Terminal window, Run development server
make dev

# Access the server at http://127.0.0.1:5000. (Make sure SERVER_NAME in .env matches current server name)
```

### Production

You need a few more things:
* A VPS with a decent provider
* Nginx
* Certbot / Letsencrypt

Below is a set of commands you can follow to get setup. I used Ubuntu 20.04 on Digital Ocean. Run the below commands as root or prepend `sudo`.

```
# install nginx
apt-get install nginx -y

# install certbot
apt-get install certbot -y

# point DNS records at your VPS w/ a domain you control

# generate diffie hellman keys
openssl dhparam -out /etc/ssl/certs/dhparam.pem 2048

# setup nginx ssl config from this repo
cp conf/nginx-ssl.conf /etc/nginx/conf.d/ssl.conf

# setup nginx site config from this repo
cp conf/nginx-site.conf /etc/nginx/sites-enabled/metachecker.io.conf

# generate TLS certificates
service nginx stop
certbot certonly --standalone -d <your dns record> --agree-tos -m <your email> -n
service nginx start

# setup ipfs service account and storage location
useradd -m ipfs
mkdir -p /opt/ipfs
chown ipfs:ipfs /opt/ipfs

# setup ipfs service daemon
cp conf/ipfs.service /etc/systemd/system/ipfs.service
systemctl daemon-reload
systemctl enable ipfs
systemctl start ipfs

# setup metachecker service account and storage location
useradd -m metachecker
mkdir -p /opt/metachecker

# setup metachecker application
git clone https://github.com/art101nft/metachecker /opt/metachecker
cp /opt/metachecker/env-example /opt/metachecker/.env
vim /opt/metachecker/.env
chown -R metachecker:metachecker /opt/metachecker

# setup metachecker service daemon
cp conf/metachecker.service /etc/systemd/system/metachecker.service
systemctl daemon-reload
systemctl enable metachecker
systemctl start metachecker

# setup ongoing syncing with remote servers and Avalanche network
crontab -u metachecker conf/crontab
```

At this point you should have Nginx web server running with TLS certificates generated with Letsencrypt/Certbot, Systemd services for IPFS daemon for serving files and Gunicorn for serving the Flask application.

You'll obviously need to update some of your configuration files to match your domain/DNS, but it's fairly trivial.

Reach out on Twitter or Discord if you need support.
