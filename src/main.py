import click

from database.config import init_db
from views.auth import auth
from views.client import client


@click.group()
def cli():
    """Application de gestion CRM Epic Events"""
    pass

@cli.command()
def init():
    """Initialiser la base de données"""
    init_db()
    click.echo("Base de données initialisée!")

cli.add_command(auth)
cli.add_command(client)

if __name__ == "__main__":
    cli()