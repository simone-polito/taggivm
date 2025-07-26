import sqlite3
from pathlib import Path
import json
from contextlib import contextmanager

DB_PATH = Path("music.db")
SCHEMA_PATH = Path("schema.sql")
GENRE_TREE_PATH = Path("genre_tree.json")
SOURCES_PATH = Path("sources.json")

#------------ CONNENCTION CONTEXT MANAGER -----------#

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # consente di accedere ai risultati come dizionari
    try:
        yield conn  # "restituisce" la connessione al blocco `with`
        conn.commit()  # se tutto è andato bene, salva i cambiamenti
    except Exception:
        conn.rollback()  # se c'è stato un errore, annulla tutto
        raise  # rilancia l'eccezione
    finally:
        conn.close()  # chiude sempre la connessione, anche in caso di errore



#------------ DATABASE INITIALIZATION -----------#
def init_db():
    """Initialize database with schema"""
    if not DB_PATH.exists():
        with sqlite3.connect(DB_PATH) as conn:
            
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
def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_tree(cursor: sqlite3.Cursor, tree: dict, parent_id: int = None):
    """Recursively insert genres into the database"""
    for name, children in tree.items():
        # insert the genre, avoiding (name, parent_id) duplicates
        # "fam" necessary to avoid NULL parent_id issues
        cursor.execute("INSERT OR IGNORE INTO genres (name, parent_id) VALUES (?, ?)", (name, parent_id if parent_id is not None else "fam"))
        # get the genre id (whether inserted now or already existed)
        cursor.execute("SELECT id FROM genres WHERE name = ? AND parent_id IS ?", (name, parent_id if parent_id is not None else "fam"))
        genre_id = cursor.fetchone()[0]

        # insert children recursively
        insert_tree(cursor, children, genre_id)

def insert_genre_tree():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        genre_tree = load_json(GENRE_TREE_PATH)
        insert_tree(cursor, genre_tree)
        conn.commit()

def insert_sources():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        sources = load_json(SOURCES_PATH)
        for source in sources:
            cursor.execute("INSERT OR IGNORE INTO sources (name, url) VALUES (?, ?)", (source['name'], source['url']))
        conn.commit()


def main():
    
    init_db()
    insert_genre_tree() 
    insert_sources()

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM genres")
        print("Numero totale di righe in genres:", cursor.fetchone()[0])

        cursor.execute("SELECT name,id,parent_id FROM genres WHERE parent_id = ?", ("fam",))
        print(cursor.fetchall())
        cursor.execute("SELECT name,id,parent_id FROM genres WHERE name = ?", ("Post-Punk",))
        print(cursor.fetchall())

        cursor = conn.execute("SELECT * FROM sources LIMIT 40")
        print(cursor.fetchall())
        cursor = conn.execute("SELECT * FROM genres LIMIT 10")
        print(cursor.fetchone())
        print(cursor.fetchall())
        print(cursor.fetchall())


if __name__ == "__main__":
    main()
