#!/bin/bash

# Script to set up dependencies for Django on Vagrant.

PG_VERSION=9.4
# Edit the following to change the name of the database user that will be created:
APP_DB_USER=myapp
APP_DB_PASS=dbpass

# Edit the following to change the name of the database that is created (defaults to the user name)
APP_DB_NAME=$APP_DB_USER


print_db_usage () {
  echo "Your PostgreSQL database has been setup and can be accessed on your local machine on the forwarded port (default: 15432)"
  echo "  Host: localhost"
  echo "  Port: 15432"
  echo "  Database: $APP_DB_NAME"
  echo "  Username: $APP_DB_USER"
  echo "  Password: $APP_DB_PASS"
  echo ""
  echo "Admin access to postgres user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo ""
  echo "psql access to app database user via VM:"
  echo "  vagrant ssh"
  echo "  sudo su - postgres"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost $APP_DB_NAME"
  echo ""
  echo "Env variable for application development:"
  echo "  DATABASE_URL=postgresql://$APP_DB_USER:$APP_DB_PASS@localhost:15432/$APP_DB_NAME"
  echo ""
  echo "Local command to access the database via psql:"
  echo "  PGUSER=$APP_DB_USER PGPASSWORD=$APP_DB_PASS psql -h localhost -p 15432 $APP_DB_NAME"
}

PROVISIONED_ON=/etc/vm_provision_on_timestamp
if [ -f "$PROVISIONED_ON" ]
then
  echo "VM was already provisioned at: $(cat $PROVISIONED_ON)"
  echo "To run system updates manually login via 'vagrant ssh' and run 'apt-get update && apt-get upgrade'"
  echo ""
  print_db_usage
  exit
fi

export DEBIAN_FRONTEND=noninteractive

# Need to fix locale so that Postgres creates databases in UTF-8
cp -p /vagrant_data/etc-bash.bashrc /etc/bash.bashrc
locale-gen en_GB.UTF-8
dpkg-reconfigure locales

export LANGUAGE=en_GB.UTF-8
export LANG=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8


PG_REPO_APT_SOURCE=/etc/apt/sources.list.d/pgdg.list
if [ ! -f "$PG_REPO_APT_SOURCE" ]
then
  # Add PG apt repo:
  echo "deb http://apt.postgresql.org/pub/repos/apt/ precise-pgdg main" > "$PG_REPO_APT_SOURCE"

  # Add PGDG repo key:
  wget --quiet -O - http://apt.postgresql.org/pub/repos/apt/ACCC4CF8.asc | apt-key add -
fi



# Install essential packages from Apt
./vagrant_data/apt.postgresql.org.sh
apt-get update -y
apt-get -y upgrade

# Python dev packages
apt-get install -y build-essential python-software-properties python-pip
# Dependencies for image processing with Pillow (drop-in replacement for PIL)
# supporting: jpeg, tiff, png, freetype, littlecms
apt-get install -y libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev
# Git (we'd rather avoid people keeping credentials for git commits in the repo, but sometimes we need it for pip requirements that aren't in PyPI)
apt-get install -y git elasticsearch

# install all versions of Python for testing.
add-apt-repository -y ppa:fkrull/deadsnakes
apt-get install -qq python2.7 python2.7-dev python3.4 python3.4-dev

# Postgresql

#
#apt-get -y install "postgresql-$PG_VERSION" "postgresql-contrib-$PG_VERSION" libpq-dev
#
#PG_CONF="/etc/postgresql/$PG_VERSION/main/postgresql.conf"
#PG_HBA="/etc/postgresql/$PG_VERSION/main/pg_hba.conf"
#PG_DIR="/var/lib/postgresql/$PG_VERSION/main"
#
## Edit postgresql.conf to change listen address to '*':
#sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" "$PG_CONF"
#
## Append to pg_hba.conf to add password auth:
#echo "host    all             all             all                     md5" >> "$PG_HBA"
#
## Explicitly set default client_encoding
#echo "client_encoding = utf8" >> "$PG_CONF"
#
## Restart so that all new config is loaded:
#service postgresql restart
#
#cat << EOF | su - postgres -c psql
#-- Create the database user:
#CREATE USER $APP_DB_USER WITH PASSWORD '$APP_DB_PASS';
#
#-- Create the database:
#CREATE DATABASE $APP_DB_NAME WITH OWNER=$APP_DB_USER
#                                  LC_COLLATE='en_US.utf8'
#                                  LC_CTYPE='en_US.utf8'
#                                  ENCODING='UTF8'
#                                  TEMPLATE=template0;
#EOF

# Tag the provision time:
date > "$PROVISIONED_ON"


# install java
sudo apt-get install openjdk-7-jre-headless -y


# install elasticsearch
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.4.2.deb
sudo dpkg -i elasticsearch-1.4.2.deb

# Configure Elasticsearch to automatically start during bootup :
update-rc.d elasticsearch defaults 95 10
sudo service elasticsearch start


# install head
sudo /usr/share/elasticsearch/bin/plugin -install mobz/elasticsearch-head


# virtualenv global setup
if ! command -v pip; then
    easy_install -U pip
fi
if [[ ! -f /usr/local/bin/virtualenv ]]; then
    easy_install virtualenv
fi

pip install tox

# bash environment global setup
cp -p /vagrant_data/bashrc /home/vagrant/.bashrc


# Cleanup
apt-get clean


