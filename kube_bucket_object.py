import click
import json
import os
import base64
import sys
from kubernetes import client, config
from datetime import datetime

def load_config():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

def get_bucket_name():
    'Get Bucket Name'
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("ssl-helper-bucket-name", "k8s-ssl-updater")
    data = secret.data # extract .data from the secret 
    bucketname = secret.data['ssl-helper-bucket-name'] # extract .data.password from the secret
    decoded = base64.b64decode(bucketname) # decode (base64) value from pasw
    decodedv2 = print(decoded.decode('utf-8'))
    return decodedv2

@click.command()
def get_objects():
    bucketname = get_bucket_name()
    print(bucketname)
    
if __name__ == '__main__':
    get_objects()