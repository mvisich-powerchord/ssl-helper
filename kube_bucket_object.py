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
def get_bucket():
    'Bucket Name'
    v1 = client.CoreV1Api()
    secret = v1.read_namespaced_secret("ssl-helper-bucket-name", "k8s-ssl-updater")
    print(secret)

if __name__ == '__main__':
    list_secrets()