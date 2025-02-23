import psycopg2
import psycopg2.extras
from flask import current_app, g
import click
import os

def get_db():
    if 'db' not in g:
        # db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
        db_url = os.environ.get("DATABASE_URI")
        if not db_url:
            raise RuntimeError("Brak konfiguracji bazy danych!")

        g.db = psycopg2.connect(db_url, cursor_factory=psycopg2.extras.DictCursor)

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        sql_code = f.read().decode('utf8')

    with db.cursor() as cursor:
        cursor.execute("BEGIN;")  
        cursor.execute(sql_code)  
        cursor.execute("COMMIT;")  

    db.commit()  



@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
