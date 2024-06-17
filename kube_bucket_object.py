import click
import json
import os
import base64
import sys
import logging
from kubernetes import client, config
from datetime import datetime
from google.cloud import storage

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

def get_projectid():
    'Get Project ID'
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("ssl-helper-bucket-project-id", "k8s-ssl-updater")
    data = secret.data # extract .data from the secret 
    projectid = secret.data['ssl-helper-bucket-project-id'] # extract .data.password from the secret
    decoded = base64.b64decode(projectid) # decode (base64) value from pasw
    decodedv2 = decoded.decode('utf-8')
    return decodedv2

def list_objects(bucketname):
    #from google.cloud import storage
    client = storage.Client()
    ssl_list = []
    for blob in client.list_blobs(bucketname, prefix='ssl-certs/', delimiter='/'):
      folder, file = blob.name.split('/')
      if file ==  "":
        continue
      ssl_list.append(file)
    for x in ssl_list:
      print(x)
    return ssl_list

def cert_bucket():
    global bucketname
    bucketname = get_bucket_name()
    #global projectid
    #projectid = get_projectid()
    print ("Bucket Name")
    print(bucketname)
    ssl_list = list_objects(bucketname)
    return ssl_list

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # Initialize a client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Get the blob
    blob = bucket.blob(source_blob_name)

    # Download the blob to a file
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

@click.command()
@click.option('--certfile', prompt='Select SSL File', type=click.Choice(['none'] + cert_bucket()), default='none')
def cert_helper(certfile):
    print(f"Listing secrets in namespace {certfile}:")
    download_blob(bucketname,"ssl-certs/{certfile}", certfile)













#if __name__ == '__main__':
#    cert_helper()