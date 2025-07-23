# Taggivum

Work in progress.
[GitHub-flavored Markdown](https://guides.github.com/features/mastering-markdown/)

**Development build:**
```bash
pip install -e .
```

**Wheel file build:**
```bash
python -m build --wheel
```

Evironment variables:
- `DEFAULT_MUSIC_DIR`: default directory of the music collection
    Default: `/home/music`
- `DEFAULT_DB_PATH`: (optional) path to the SQLite database file  
    Default: `music.db`

CLI commands:
- `scan`: scans the music library to initialize the database with newer albums
- `meta_fetch`: searches different metadata from multiple sources and saves them on the database