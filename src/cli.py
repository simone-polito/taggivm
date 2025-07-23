import click
from pathlib import Path

from scanner import discover_scan
from config import CONFIG_FILE, load_config, save_config



@click.group()
@click.pass_context
def cli(ctx: click.Context):
    """Taggivm CLI - A tool for tagging your music collection."""
    
    config = load_config()
    music_dir = config.get("music_directory")        

    # Context object
    ctx.ensure_object(dict)
    ctx.obj["config"] = config
    ctx.obj["music_directory"] = Path(music_dir)


## main commands

@cli.command()
@click.pass_context
#@click.argument("path", type=click.Path(exists=True))
def scan(ctx: click.Context):
    """Scan the music library to initialize new album on the database"""
    music_dir = ctx.obj["music_directory"]

    if not CONFIG_FILE.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + " No configuration found. Please set it with music directory " + click.style("config setup -m", fg="yellow", bold=True))
        return
    if not music_dir.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + f" Music directory '{music_dir}' does not exist. Please check your configuration.")
        exit(1)

    click.echo(f"Scanning directory: {music_dir}")
    scan, skip = discover_scan(music_dir)
    click.echo("Scan completed.")
    click.echo("Albums to scan:")
    for i, album in enumerate(scan, 1):
        album_name = album.name
        artist_name = album.parent.name
        click.echo(f"  {i}. {artist_name} - {album_name}")


## config commands

@cli.group()
def config():
    """Configuration options"""
    pass

@config.command()
def show():
    """Show the current configuration"""
    if not CONFIG_FILE.exists():
        click.echo(click.style("Error:", fg="red", bold=True) + " No configuration found. Please set it with music directory " + click.style("config setup -m", fg="yellow", bold=True))
        return

    config = load_config()
    click.echo(f"Music directory: {config.get('music_directory')}")

@config.command()
#@click.argument("music_directory", type=click.Path(exists=True))
@click.option("--music_directory", "-m", type=click.Path(exists=True), required=True)
def setup(music_directory: str):
    """Setup the music directory"""
    config = load_config()
    config["music_directory"] = music_directory

    save_config(config)
    click.echo(f"Music directory set to '{music_directory}'")
