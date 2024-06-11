import click
import json
import os
from kubernetes import client, config
from datetime import datetime

def load_config():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()


@click.command()
#@click.option('--namespace', prompt='Select a namespace', type=click.Choice(['all-namespaces'] + get_namespaces()), default='all-namespaces')
def list_secrets(namespace):
    'Bucket Name'
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("ssl-helper-bucket-name", "k8s-ssl-updater")
    print(secret)

if __name__ == '__main__':
    list_secrets()