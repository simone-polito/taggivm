-- Artist name decoded from album API call
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    metadata_status TEXT DEFAULT 'pending' CHECK (metadata_status IN ('pending', 'partial', 'complete', 'aggregated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO artists (id, name) VALUES (0, 'Unknown Artist');  -- dummy artist for albums initialization
-- Album data from directories
-- foreign key one(artist) to many(albums)
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY,
    artist_id INTEGER NOT NULL DEFAULT 0, -- 0 for 'Unknown Artist'
    title TEXT NOT NULL,
    release_year INTEGER,
    album_artist TEXT, -- artist name from album directory
    total_tracks INTEGER DEFAULT 0,
    path TEXT NOT NULL UNIQUE,
    metadata_status TEXT DEFAULT 'pending' CHECK (metadata_status IN ('pending', 'partial', 'complete', 'aggregated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE,
    UNIQUE (title, artist_id) -- only one album with the same title for an artist
);
-- Track data from files
-- foreign key one(album) to many(tracks)
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY,
    album_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    duration_ms INTEGER,
    fingerprint TEXT NOT NULL,-- UNIQUE,
    track_number INTEGER NOT NULL,
    disc_number INTEGER DEFAULT 1,
    format TEXT DEFAULT 'unknown' CHECK (format IN ('mp3', 'flac', 'ogg', 'wav', 'aac', 'unknown')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE
);

-- Genres in tree structure
-- self-referencing foreign key for parent genre
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER, -- reference to the parent genre (0 for main genres)
    FOREIGN KEY (parent_id) REFERENCES genres(id),
    UNIQUE(name, parent_id) -- genres can appartain to different parents (Post-Punk)
);
INSERT INTO genres (id, name) VALUES (0, 'Genre');  -- dummy genre for main genres with no parent
-- Sources of metadata
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_url TEXT UNIQUE,
    reliability_score INTEGER DEFAULT 0 CHECK (reliability_score BETWEEN 0 AND 100)
);

-- Metadata search tasks for albums/artist manager (maybe also for tracks)
-- CREATE TABLE IF NOT EXISTS api_queries_albums (
--     id INTEGER PRIMARY KEY,
--     status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'done', 'error'
--     endpoint TEXT NOT NULL, -- API endpoint used for the query (url:=base_url + endpoint)
--     parameters TEXT,  -- JSON: {"query":"Yung Lean","limit":5}
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     source_id INTEGER NOT NULL,
--     album_id INTEGER NOT NULL,
--     UNIQUE (album_id, source_id),
--     FOREIGN KEY (album_id) REFERENCES albums(id),
--     FOREIGN KEY (source_id) REFERENCES sources(id)
-- );
-- CREATE TABLE IF NOT EXISTS api_queries_artists (
--     id INTEGER PRIMARY KEY,
--     status TEXT DEFAULT 'pending',
--     endpoint TEXT NOT NULL, 
--     parameters TEXT,  
--     source_id INTEGER NOT NULL,
--     artist_id INTEGER NOT NULL,
--     UNIQUE (artist_id, source_id),
--     FOREIGN KEY (artist_id) REFERENCES artists(id),
--     FOREIGN KEY (source_id) REFERENCES sources(id)
-- );
CREATE TABLE IF NOT EXISTS api_queries (
    id INTEGER PRIMARY KEY,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('artist', 'album', 'track')),
    entity_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'done', 'error')),
    endpoint TEXT NOT NULL,
    parameters TEXT, -- JSON
    response_data TEXT, -- JSON response
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id),
    UNIQUE (entity_type, entity_id, source_id)
);
-- Metadata api cache for albums7artist
-- CREATE TABLE api_cache_albums (
--     id INTEGER PRIMARY KEY,
--     response_data TEXT NOT NULL, -- Could be JSON or raw response
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     query_id INTEGER NOT NULL,
--     FOREIGN KEY (query_id) REFERENCES api_queries_albums(id)
-- );
-- CREATE TABLE api_cache_artists (
--     id INTEGER PRIMARY KEY,
--     response_data TEXT NOT NULL,
--     updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     query_id INTEGER NOT NULL,
--     FOREIGN KEY (query_id) REFERENCES api_queries_artists(id)
-- );


-- Metadata from sources about artists-albums-tracks
-- Many-to-many relationship between sources and artists-albums-tracks but unique
CREATE TABLE IF NOT EXISTS artist_metadata(
    id INTEGER PRIMARY KEY,
    type TEXT, -- 'solo', 'band', 'collaboration'
    artist_name TEXT,
    real_name TEXT,
    aliases TEXT,
    birth_date TEXT,
    birth_place TEXT,
    death_date TEXT,
    residence_place TEXT,
    member_of TEXT,
    formation_year INTEGER,
    disbanded_year INTEGER,
    members_roles TEXT,
    n_albums INTEGER,
    image_url TEXT,
    followers INTEGER,
    site_url TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    artist_id INTEGER NOT NULL,
    query_id INTEGER NOT NULL,
    UNIQUE (artist_id, query_id),
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (query_id) REFERENCES api_queries(id)
);
CREATE TABLE IF NOT EXISTS album_metadata(
    id INTEGER PRIMARY KEY,
    title TEXT,
    album_artist TEXT,
    album_title TEXT,
    type TEXT,
    ranking REAL,
    views INTEGER,
    release_date TEXT,
    recording_date TEXT,
    descriptors TEXT,
    language TEXT,
    length TEXT,
    media_links TEXT,
    site_url TEXT,
    cover_url TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    album_id INTEGER NOT NULL,
    query_id INTEGER NOT NULL,
    UNIQUE (album_id, query_id),
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (query_id) REFERENCES api_queries(id)
);
CREATE TABLE IF NOT EXISTS track_metadata(
    id INTEGER PRIMARY KEY,
    title TEXT,
    artist TEXT,
    feat TEXT,
    with TEXT,
    track_number TEXT,
    ranking REAL,
    views INTEGER,
    credits TEXT,
    lyrics TEXT,
    length TEXT,
    fingerprint TEXT,
    site_url TEXT,
    cover_url TEXT, -- ??
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    track_id INTEGER NOT NULL,
    query_id INTEGER NOT NULL,
    UNIQUE (track_id, query_id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    FOREIGN KEY (query_id) REFERENCES api_queries(id)
);

-- Many-to-many relationship between genres, artists-albums-tracks and sources from metadata
CREATE TABLE IF NOT EXISTS artist_genres_metadata (
    genre_id INTEGER NOT NULL,
    metadata_id INTEGER NOT NULL,
    role TEXT DEFAULT 'main' CHECK (role IN ('main', 'secondary', 'influence', 'style')),
    PRIMARY KEY (genre_id, metadata_id),
    FOREIGN KEY (metadata_id) REFERENCES artist_metadata(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    UNIQUE (metadata_id, genre_id, role)
);
CREATE TABLE IF NOT EXISTS album_genres_metadata (
    genre_id INTEGER NOT NULL,
    metadata_id INTEGER NOT NULL,
    role TEXT DEFAULT 'main' CHECK (role IN ('main', 'secondary', 'influence', 'style')),
    PRIMARY KEY (genre_id, metadata_id),
    FOREIGN KEY (metadata_id) REFERENCES album_metadata(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    UNIQUE (metadata_id, genre_id, role)
);
CREATE TABLE IF NOT EXISTS track_genres_metadata (
    genre_id INTEGER NOT NULL,
    metadata_id INTEGER NOT NULL,
    role TEXT DEFAULT 'main' CHECK (role IN ('main', 'secondary', 'influence', 'style')),
    PRIMARY KEY (genre_id, metadata_id),
    FOREIGN KEY (metadata_id) REFERENCES track_metadata(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    UNIQUE (metadata_id, genre_id, role)
);

-- Final metadata for tags 
CREATE TABLE IF NOT EXISTS final_artists_metadata(
    name TEXT NOT NULL,
    country TEXT,
    metadata_status TEXT,
    artist_id INTEGER PRIMARY KEY,
    FOREIGN KEY (artist_id) REFERENCES artists(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS final_albums_metadata(
    title TEXT NOT NULL,
    year INTEGER,
    genres TEXT,
    styles TEXT,
    metadata_status TEXT,
    album_artist_id INTEGER NOT NULL,
    album_id INTEGER PRIMARY KEY,
    FOREIGN KEY (album_artist_id) REFERENCES artists(id),
    FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS final_tracks_metadata(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    track_number INTEGER,
    metadata_status TEXT,
    album_id INTEGER NOT NULL,
    track_artist_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (track_artist_id) REFERENCES artists(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id) ON DELETE CASCADE
);

-------- FIXED DATA ---------------------

-- sources
-- INSERT INTO sources (name, url) 
--     VALUES 
--         ('RYM', 'https://rateyourmusic.com'),
--         ('Genius', 'https://genius.com'),
--         ('Discogs', 'https://www.discogs.com'),
--         ('Spotify', 'https://open.spotify.com'),
--         ('Wikipedia', 'https://wikipedia.org'),
--         ('MusicBrainz', 'https://musicbrainz.org');

-- genres
-- -- Generi principali
-- INSERT OR IGNORE INTO genres (name, parent_id) VALUES
--     ('Rock', NULL),
--     ('Pop', NULL),
--     ('Hip-Hop', NULL),
--     ('Jazz', NULL),
--     ('Classical', NULL),
--     ('Electronic', NULL);

-- -- Sottogeneri di Electronic
-- INSERT OR IGNORE INTO genres (name, parent_id)
-- VALUES
--     ('House', NULL),
--     ('Techno', NULL),
--     ('Trance', NULL),
--     ('Drum and Bass', NULL),
--     ('Dubstep', NULL);

-- -- Assegna il parent_id dinamicamente
-- UPDATE genres SET parent_id = (SELECT id FROM genres WHERE name = 'Electronic')
-- WHERE name IN ('House', 'Techno', 'Trance', 'Drum and Bass', 'Dubstep');


-- Per ricerche frequenti su nome
CREATE INDEX idx_artists_name ON artists(name);
CREATE INDEX idx_albums_title ON albums(title);
CREATE INDEX idx_tracks_title ON tracks(title);

-- Per query su stato dei metadati
CREATE INDEX idx_artists_metadata_status ON artists(metadata_status);
CREATE INDEX idx_albums_metadata_status ON albums(metadata_status);

-- Per join frequenti
CREATE INDEX idx_albums_artist_id ON albums(artist_id);
CREATE INDEX idx_tracks_album_id ON tracks(album_id);

-- Per le query API
CREATE INDEX idx_api_queries_status ON api_queries(status);

-- Per le ricerche nei metadati
CREATE INDEX idx_artist_metadata_artist_id ON artist_metadata(artist_id);
CREATE INDEX idx_album_metadata_album_id ON album_metadata(album_id);
CREATE INDEX idx_track_metadata_track_id ON track_metadata(track_id);

-- Per la gerarchia dei generi
CREATE INDEX idx_genres_parent_id ON genres(parent_id);