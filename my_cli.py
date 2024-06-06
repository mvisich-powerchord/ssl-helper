import click
import os

@click.group()
def cli():
    'A minimalistic script to check file existence'
    pass

@cli.command()
@click.argument('file_path')
def check_file(file_path):
    'Check if a file exists in the current directory'
    if os.path.exists(file_path):
        click.echo(f"The file {file_path} exists.")
    else:
        click.echo(f"The file {file_path} does not exist.")

if __name__ == '__main__':
    cli()
