import click
from pathlib import Path

from scanner import discover_scan
from config import MUSIC_LIBRARY_PATH


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Taggivm CLI - A tool for tagging your music collection."""
    
    # context object
    ctx.ensure_object(dict)
    ctx.obj["music_directory"] = Path(MUSIC_LIBRARY_PATH)


## Main Commands

@cli.command()
@click.pass_context
#@click.argument("path", type=click.Path(exists=True))
def scan(ctx: click.Context):
    """Scan the music library to initialize new album on the database"""
    music_dir = ctx.obj["music_directory"]

    if not music_dir.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + f" Music directory '{music_dir}' does not exist. Please check the env variable " + click.style("MUSIC_LIBRARY_PATH", fg="yellow", bold=True))
        exit(1)

    click.echo(f"Scanning directory: {music_dir}")
    scan, skip = discover_scan(music_dir)
    click.echo("Scan completed.")
    click.echo("Albums to scan:")
    for i, album in enumerate(scan, 1):
        album_name = album.name
        artist_name = album.parent.name
        click.echo(f"  {i}. {artist_name} - {album_name}")