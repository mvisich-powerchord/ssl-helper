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

def get_namespaces():
    file_path = "namespaces-list.json"
    if os.path.exists(file_path) and (datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))).seconds < 300:
        with open(file_path, 'r') as file:
            return json.load(file)
    
    load_config()
    v1 = client.CoreV1Api()
    namespaces = [ns.metadata.name for ns in v1.list_namespace().items]

    with open(file_path, 'w') as file:
        json.dump(namespaces, file)

    return namespaces

def get_secrets_list(namespace='all-namespaces'):
    load_config()
    v1 = client.CoreV1Api()
    secrets = []

    if namespace == 'all-namespaces':
        selected_namespaces = get_namespaces()
    else:
        selected_namespaces = [namespace]
    for ns in selected_namespaces:
        k8s_secrets = v1.list_namespaced_secret(namespace=ns)
        secrets = secrets + [{'name': x.metadata.name, 'namespace': ns} for x in k8s_secrets.items]

    return secrets

@click.command()
@click.option('--namespace', prompt='Select a namespace', type=click.Choice(['all-namespaces'] + get_namespaces()), default='all-namespaces')
def list_secrets(namespace):
    'List the names of all secrets in the selected namespace or all namespaces'
    secrets = get_secrets_list(namespace)
    print(f"Listing secrets in namespace {namespace}:")
    for s in secrets:
        print(s)

if __name__ == '__main__':
    list_secrets()