import click
from kube_secrets_list import get_secrets_list
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

def parse_secret_name(secret_name_str):
    return json.loads(secret_name_str.replace("'", '"'))

def create_temp_directory(secret_name):
    current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    temp_dir = tempfile.mkdtemp(prefix=f"{secret_name}_at_{current_datetime}_")
    return temp_dir

def write_pfx_file(temp_dir, pfx_file):
    pfx_path = os.path.join(temp_dir, "my.pfx")
    with open(pfx_path, 'wb') as file:
        file.write(pfx_file)
    return pfx_path

def execute_openssl_command(command, working_directory):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=working_directory)
    return result.returncode, result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

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

def validate_modulus(key_path, cert_path, temp_dir):
    key_modulus_command = f"openssl rsa -noout -modulus -in {key_path} | openssl md5"
    cert_modulus_command = f"openssl x509 -noout -modulus -in {cert_path} | openssl md5"
    key_modulus = execute_openssl_command(key_modulus_command, temp_dir)
    cert_modulus = execute_openssl_command(cert_modulus_command, temp_dir)
    return key_modulus, cert_modulus

def validate_dates(cert_path, temp_dir, password=None):
    passin_option = f" -passin pass:{password}" if password else ""
    start_date_command = f"openssl x509 -noout -startdate -in {cert_path}{passin_option}"
    end_date_command = f"openssl x509 -noout -enddate -in {cert_path}{passin_option}"
    
    return_code_start, start_date_str, _ = execute_openssl_command(start_date_command, temp_dir)
    return_code_end, end_date_str, _ = execute_openssl_command(end_date_command, temp_dir)

    start_date_str = start_date_str.split('=', 1)[1].strip()
    end_date_str = end_date_str.split('=', 1)[1].strip()
    
    start_date = datetime.strptime(start_date_str, '%b %d %H:%M:%S %Y %Z')
    end_date = datetime.strptime(end_date_str, '%b %d %H:%M:%S %Y %Z')
    
    return start_date, end_date

def backup_secret(secret_name, namespace):
    load_config()
    v1 = client.CoreV1Api()
    old_secret = v1.read_namespaced_secret(secret_name, namespace)

    # Create a copy of the old secret under a different name
    backup_secret_name = f"{secret_name}-backup-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    backup_secret = client.V1Secret(
        metadata=client.V1ObjectMeta(name=backup_secret_name),
        type=old_secret.type,
        data=old_secret.data
    )
    v1.create_namespaced_secret(namespace, backup_secret)

    # Generate bash command string to restore the backed up secret
    restore_command = (
        f"kubectl get secret {backup_secret_name} -n {namespace} -o yaml > {backup_secret_name}.secret.yaml; "
        f"kubectl delete secret {secret_name} -n {namespace}; "
        f"kubectl apply -f {backup_secret_name}.secret.yaml;"
    )

    return restore_command


def create_and_replace_tls_secret(key_path, cert_path, secret_name, namespace):
    load_config()
    v1 = client.CoreV1Api()

    # Read the existing secret to preserve any other data
    existing_secret = v1.read_namespaced_secret(secret_name, namespace)

    # Update the secret with new key and cert data
    with open(key_path, 'r') as key_file, open(cert_path, 'r') as cert_file:
        existing_secret.data["tls.key"] = base64.b64encode(key_file.read().encode()).decode()
        existing_secret.data["tls.crt"] = base64.b64encode(cert_file.read().encode()).decode()

    # Replace the existing secret
    return v1.replace_namespaced_secret(secret_name, namespace, existing_secret)

@click.command()
@click.option('--certfile', prompt='Select SSL File For GCP Storage Bucket', type=click.Choice(['none'] + cert_bucket()), default='none')
@click.option('--secretname', type=click.Choice(list(map(str, get_secrets_list()))), prompt='Select a secret', help='The name of the secret to update')
@click.option('--pfxcode', type=click.STRING, prompt=True, hide_input=True, confirmation_prompt=False, help='Password for the PFX file', required=False)
#def update_secret_bucket(secret_name, pfx_file, password_required, password):
def update_secret_bucket(certfile,secretname,pfxcode):
    'Update the specified Kubernetes secret with PFX file uplodated to GCP bucket'
    print("here")

    # validate the cert and key match


