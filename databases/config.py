from __future__ import absolute_import

import click
from flask.cli import with_appcontext
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy, declarative_base
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import MetaData
from flask_migrate import Migrate

dbase = SQLAlchemy()
engine = None
migrate = Migrate()

Base = declarative_base()
session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
# session = scoped_sess(dbase)


def initializer(key, kwargs):
    if kwargs.keys().__contains__(key):
        return kwargs[key]
    return None


@click.command("populate")
@click.option("--tables", default="all")
@with_appcontext
def populate_tables(tables):
    click.echo("Populating tables: {}".format(tables))
    initialize_dbase(current_app)


@click.command("delete")
@click.option("--tables", default="all")
@with_appcontext
def erase_tables(tables):
    click.echo("Deleting tables: {}".format(tables))
    delete()


def initialize_dbase(app):
    # dbase.init_app(app)
    engine = dbase.get_engine(app)
    session.configure(bind=engine)
    migrate.init_app(app, dbase)
    dbase.create_all(bind="__all__", app=app)
    app.cli.add_command(populate_tables)
    app.cli.add_command(erase_tables)


def delete():
    dbase.drop_all()
    click.echo("Done!")
