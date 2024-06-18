import click
from kube_secrets_list import list_secrets
from kube_secret_update import update_secret
from kube_bucket_object import cert_helper
from kube_validate_cert import cert_validate
from my_cli import check_file

@click.group()
def cli():
    'Kubernetes SSL updater'
    pass

cli.add_command(list_secrets, name='list-secrets')
cli.add_command(update_secret, name='update-secret')
cli.add_command(check_file, name='check-file')
cli.add_command(cert_helper, name='cert-helper')
cli.add_command(cert_validate, name='cert-validate')


if __name__ == '__main__':
    cli()
