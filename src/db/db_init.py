import sqlite3
from pathlib import Path
import json
from contextlib import contextmanager
from .domain.path import SCHEMA_PATH, GENRE_TREE_PATH, SOURCES_PATH

#------------ CONNENCTION CONTEXT MANAGER -----------#

@contextmanager
def get_connection(db_path: Path) :
    conn = sqlite3.connect(db_path)
    try:
        yield conn  # "restituisce" la connessione al blocco `with`
        conn.commit()  # se tutto è andato bene, salva i cambiamenti
    except Exception:
        conn.rollback()  # se c'è stato un errore, annulla tutto
        raise  # rilancia l'eccezione
    finally:
        conn.close()  # chiude sempre la connessione, anche in caso di errore

#------------ DATABASE INITIALIZATION -----------#

def init_db(db_path: Path):
    """Initialize the database with the schema and static data"""
    with get_connection(db_path) as conn:
        _init_schema(conn)
        _insert_genre_tree(conn)
        _insert_sources(conn)


def _init_schema(conn: sqlite3.Connection):
    """Initialize database with schema"""
    # set pragmas: must be set for every connection at the beginning
    conn.execute("PRAGMA journal_mode = WAL") # Write-Ahead Logging, better concurrency
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    conn.execute("PRAGMA synchronous = NORMAL") # Balance between performance and safety
    #conn.row_factory = sqlite3.Row  # Permette l'accesso alle colonne come chiavi
    
    # execute schema
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    
    # apply migrations
    _apply_migrations(conn)

def _apply_migrations(conn: sqlite3.Connection):
    """Migration handler"""
    # sfrutta PRAGMA user_version;
    pass

#------------ STATIC DATA INSERTION -----------#
def _load_json(path: Path) -> dict:
    """Load JSON data from a file as dictionary"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _insert_tree(cursor: sqlite3.Cursor, tree: dict, parent_id: int = None):
    """Recursively insert genres into the database"""
    for name, children in tree.items():
        # insert the genre, avoiding (name, parent_id) duplicates
        # 0 necessary to avoid NULL parent_id issues
        cursor.execute("INSERT OR IGNORE INTO genres (name, parent_id) VALUES (?, ?)", (name, parent_id if parent_id is not None else 0))
        # get the genre id (whether inserted now or already existed)
        cursor.execute("SELECT id FROM genres WHERE name = ? AND parent_id IS ?", (name, parent_id if parent_id is not None else 0))
        genre_id = cursor.fetchone()[0]

        # insert children recursively
        _insert_tree(cursor, children, genre_id)

def _insert_genre_tree(conn: sqlite3.Connection):
    """Insert genre tree from JSON file into the database"""
    cursor = conn.cursor()
    genre_tree = _load_json(GENRE_TREE_PATH)
    _insert_tree(cursor, genre_tree)

def _insert_sources(conn: sqlite3.Connection):
    """Insert sources from JSON file into the database"""
    cursor = conn.cursor()
    sources = _load_json(SOURCES_PATH)
    for source in sources:
        cursor.execute("INSERT OR IGNORE INTO sources (name, base_url) VALUES (?, ?)", (source['name'], source['base_url']))

def update_genre_tree(conn: sqlite3.Connection):
    """Update the genre tree from the JSON file"""
    pass

def update_sources(conn: sqlite3.Connection):
    """Update the sources from the JSON file"""
    pass
