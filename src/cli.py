import click
from pathlib import Path

from core import MUSIC_LIBRARY_PATH, DB_PATH
from db import init_db
from services import discover_scan, init_album_DB

SKIP_INIT_DB_COMMANDS = {"init", "help", "version"}

@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Taggivm CLI - A tool for tagging your music collection."""
    
    # context object
    ctx.ensure_object(dict)
    ctx.obj["music_directory"] = Path(MUSIC_LIBRARY_PATH)
    ctx.obj["db_path"] = Path(DB_PATH)

    if ctx.invoked_subcommand in SKIP_INIT_DB_COMMANDS:
        return

    if not DB_PATH.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + f" Database file '{DB_PATH}' not found. Run `taggivm init` first.")
        exit(1)
    # eventually check the if the schema is right (see below for better implementation)


## Main Commands

@cli.command()
@click.pass_context
#@click.argument("path", type=click.Path(exists=True))
def scan(ctx: click.Context):
    """Scan the music library to initialize new album on the database"""
    music_dir = ctx.obj["music_directory"]
    db_path = ctx.obj["db_path"]

    if not music_dir.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + f" Music directory '{music_dir}' does not exist. Please check the env variable " + click.style("MUSIC_LIBRARY_PATH", fg="yellow", bold=True))
        exit(1)

    click.echo(f"Scanning directory: {music_dir}")
    scan_tree = discover_scan(music_dir)
    click.echo("Scan completed.")
    click.echo("Albums to initialize:")
    for artist, albums in scan_tree.items():
        click.echo(f"  {artist}:")
        for album, path in albums.items():
            click.echo(f"    - {album} ({path})")
    init_album_DB(scan_tree, db_path)
    click.echo("All albums initialized successfully.")

@cli.command()
@click.pass_context
def init(ctx: click.Context):
    """Initialize the album database."""
    db_path = ctx.obj["db_path"]

    if db_path.exists():
        confirm = click.confirm(
            click.style(f"Database file '{db_path}' already exists. Do you want to re-initialize it (this will delete all data)?", fg="yellow", bold=True),
            default=False
        )
        if not confirm:
            click.echo(click.style("Initialization cancelled.", fg="red"))
            exit(0)
        try:
            db_path.unlink()
            click.echo(click.style(f"Deleted existing database: {db_path}", fg="yellow"))
        except Exception as e:
            click.echo(click.style("Error deleting database: ", fg="red", bold=True) + str(e))
            exit(1)

    try:
        click.echo(f"Initializing database: {db_path}")
        init_db(db_path)
        click.echo(click.style("Database initialization completed.", fg="green"))
    except Exception as e:
        # cleanup file if created
        if db_path.exists():
            db_path.unlink()
        click.echo(click.style("Error during initialization: ", fg="red", bold=True) + str(e))
        exit(1)



## TODO
##################### Decorator @require_db per comandi che usano il DB
# import functools
# def require_db(f):
#     @functools.wraps(f)
#     @click.pass_context
#     def wrapper(ctx, *args, **kwargs):
#         db_path = Path(DB_PATH)

#         if not db_path.exists():
#             click.echo(click.style("Error:", fg="red", bold=True) + f" Database '{db_path}' not found. Run `taggivm init` first.")
#             ctx.exit(1)

#         # (Opzionale) Verifica struttura minima del DB
#         try:
#             conn = sqlite3.connect(db_path)
#             conn.execute("SELECT 1 FROM albums LIMIT 1")  # verifica tabella 'albums'
#         except sqlite3.DatabaseError as e:
#             click.echo(click.style("Invalid database:", fg="red") + f" {e}")
#             ctx.exit(1)
#         finally:
#             conn.close()

#         return ctx.invoke(f, *args, **kwargs)
#     return wrapper

# @cli.command()
# @require_db
# @click.pass_context
# def scan(ctx):
#     """Scan your music library."""
#     ...
