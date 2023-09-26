import mysql.connector
import sqlparse

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host=current_app.config["DATABASE"]["host"],
            user=current_app.config["DATABASE"]["user"],
            password=current_app.config["DATABASE"]["password"],
            database=current_app.config["DATABASE"]["database"]
        )

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        cursor = db.cursor()
        statements = sqlparse.split(f.read().decode('utf8'))
        for statement in statements:
            try:
                cursor.execute(statement)
            except mysql.connector.Error as err:
                print(f"MySQL Error: {err}")
                db.rollback()
    cursor.close()


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)