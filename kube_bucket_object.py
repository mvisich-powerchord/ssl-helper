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
    sec = v1.read_namespaced_secret("ssl-helper-bucket-name", "k8s-ssl-updater")
    secret_base64 = base64.b64decode(sec.strip().split()[1].translate(None, '}\''))
    print(secret_base64)

if __name__ == '__main__':
    list_secrets()