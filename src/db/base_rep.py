import sqlite3
from contextlib import contextmanager
from typing import Iterator, Dict, Any, List, Optional
from datetime import datetime

class BaseRepository:
    #_initialized = False 
    def __init__(self, db_path: str):
        self.db_path = db_path
        # decidi se gestire inizializzazione tramite creazione repo o separatamente
        # if not BaseRepository._initialized:
        #     self._initialize_database()
        #     BaseRepository._initialized = True

    def _initialize_database(self):
        """Initialize the database with the schema"""
        pass
    
    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        # pragmas ? 
        conn.row_factory = sqlite3.Row  # allow dictionary-like access
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    # @contextmanager
    # def _cursor(self, conn: Optional[sqlite3.Connection] = None) -> Iterator[sqlite3.Cursor]:
    #     """Context manager for cursors (can reuse existing connection)"""
    #     if conn:
    #         yield conn.cursor()
    #     else:
    #         with self._connection() as conn:
    #             with conn:
    #                 yield conn.cursor()

    def _execute(self, query: str, params: tuple = (), commit: bool = False) -> sqlite3.Cursor:
        """Execute a query and return the cursor"""
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            if commit:
                conn.commit()
            return cursor

    def _execute_many(self, query: str, params_list: List[tuple], commit: bool = False) -> sqlite3.Cursor:
        """Execute many queries (multiple rows) and return the cursor"""
        with self._get_connection() as conn:
            cursor = conn.executemany(query, params_list)
            if commit:
                conn.commit()
            return cursor

    def _fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Execute a query and fetch a single row"""
        cursor = self._execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def _fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and fetch all rows"""
        cursor = self._execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
            
    def _insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a new record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        params = tuple(data.values())
        cursor = self._execute(query, params, commit=True)
        return cursor.lastrowid # return the new record's ID
    
    def _insert_many(self, table: str, data_list: List[Dict[str, Any]]) -> List[int]:
        """Insert multiple records (same columns, same table)"""
        columns = ', '.join(data_list[0].keys())
        placeholders = ', '.join(['?'] * len(data_list[0]))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        params_list = [tuple(data.values()) for data in data_list]
        cursor = self._execute_many(query, params_list, commit=True)
        return cursor.lastrowid # seems to return None
        
    def _update(self, table: str, id_value: Any, id_field: str, data: Dict[str, Any]) -> bool:
        """Update an existing record by ID"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause}, updated_at = ? WHERE {id_field} = ?"
        values = list(data.values())
        values.append(datetime.now().isoformat()) # ???necessary???
        values.append(id_value)
        cursor = self._execute(query, tuple(values), commit=True)
        return cursor.rowcount > 0 # check if the update was successful
    
    def _delete(self, table: str, id_value: Any, id_field: str = 'id') -> bool:
        """Delete a record by ID"""
        query = f"DELETE FROM {table} WHERE {id_field} = ?"
        cursor = self._execute(query, (id_value,), commit=True)
        return cursor.rowcount > 0

    
    
#---- SCARTI / BONUS

    # def _exists(self, table: str, id_value: Any, id_field: str = 'id') -> bool: # ???necessary???
    #     """Check if a record exists by ID"""
    #     query = f"SELECT 1 FROM {table} WHERE {id_field} = ? LIMIT 1"
    #     return self._fetch_one(query, (id_value,)) is not None
    


# def _execute(self, query: str, params: tuple = (), *, commit: bool = False,conn: Optional[sqlite3.Connection] = None) -> sqlite3.Cursor:
#     """Esegue una query con controllo opzionale del commit.
    
#     Args:
#         conn: Se passata, usa questa connessione esistente invece di crearne una nuova
#         commit: Se True, fa commit automatico (solo se conn è None)
#     """
#     should_close = False
#     if conn is None:
#         conn = self._get_connection()
#         should_close = True
    
#     try:
#         cursor = conn.execute(query, params)
#         if commit and should_close:
#             conn.commit()
#         return cursor
#     except Exception:
#         if should_close:
#             conn.rollback()
#         raise
#     finally:
#         if should_close:
#             conn.close()

# # Singola modifica atomica (commit automatico ok)
# self._execute(
#     "UPDATE artists SET name = ? WHERE artist_id = ?",
#     (new_name, artist_id),
#     commit=True
# )

# # Parte di una transazione complessa (no commit)
# with self._get_connection() as conn:
#     self._execute(query1, params1, conn=conn, commit=False)
#     self._execute(query2, params2, conn=conn, commit=False)
#     conn.commit()