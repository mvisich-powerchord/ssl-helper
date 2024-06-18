#!/bin/sh

# Ensure Python and pip are installed
apk add --no-cache python3 py3-pip openssl

# remove /usr/bin/python
echo "here"

# Create a symbolic link for python
ln -s /usr/bin/python3 /usr/bin/python

# Upgrade pip
pip3 install --upgrade pip


python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r ./requirements.txt

# Run the web interface
exec python ./web_interface.py