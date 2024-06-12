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


@click.command()
def get_bucket():
    'Bucket Name'
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("ssl-helper-bucket-name", "k8s-ssl-updater")
    print(secret)


    data = secret.data # extract .data from the secret 
    print(data)
    bucketname = secret.data['ssl-helper-bucket-name'] # extract .data.password from the secret
    print(bucketname)
    decoded = base64.b64decode(bucketname) # decode (base64) value from pasw
    
    print(decoded.decode('utf-8'))





    #secret_base64 = base64.b64decode(sec.strip().split()[1].translate(None, '}\''))
    #secret_base64 = base64.b64decode(sec["ssl-helper-bucket-name"])
    #print(secret_base64)

if __name__ == '__main__':
    list_secrets()