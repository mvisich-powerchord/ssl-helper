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
    decodedv2 = decoded.decode('utf-8')
    return decodedv2

def list_objects(bucketname):
    from google.cloud import storage
    client = storage.Client()
    ssl_list = []
    for blob in client.list_blobs(bucketname, prefix='ssl-certs/', delimiter='/'):
      folder, file = blob.name.split('/')
      if file ==  "":
        continue
      ssl_list.append(file)
    return ssl_list

def cert_bucket():
    bucketname = get_bucket_name()
    list_objects(bucketname)

@click.command()
#@click.option('--cert-file', prompt='Select a cert', type=click.Choice(['none'] + cert_bucket()), default='none')


#if __name__ == '__main__':
#    get_objects()