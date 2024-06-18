import click
import json
import os
import base64
import sys
import logging
import tempfile
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

def list_objects(bucketname):
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
    print ("Bucket Name")
    print(bucketname)
    ssl_list = list_objects(bucketname)
    return ssl_list

def download_blob(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(f"Blob {source_blob_name} downloaded to {destination_file_name}.")

def extract_key(pfx_path, temp_dir, password=None):
    command = f"openssl pkcs12 -in {pfx_path} -legacy -nocerts -out my.key -nodes"
    if password:
        command += f" -passin pass:{password}"
    return execute_openssl_command(command, temp_dir)

def extract_certificate(pfx_path, temp_dir, password=None):
    command = f"openssl pkcs12 -legacy -nodes -in {pfx_path} -nokeys -out my.crt"
    if password:
        command += f" -passin pass:{password}"
    return execute_openssl_command(command, temp_dir)

def create_temp_directory(certfile):
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = tempfile.mkdtemp(prefix=f"{certfile}_at_{current_datetime}_")
    return temp_dir


@click.command()
@click.option('--certfile', prompt='Select SSL File', type=click.Choice(['none'] + cert_bucket()), default='none')
def cert_validate(certfile):
    print(f"validating certfile for {certfile}:")
    certfilepath = "ssl-certs/{}".format(certfile)
    temp_dir = create_temp_directory(certfile)
    print(temp_dir)
    download_blob(bucketname,certfilepath,certfile)





    # validate the cert and key match


