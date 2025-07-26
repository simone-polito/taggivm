-- Artist data from directories but rightly formatted 
CREATE TABLE IF NOT EXISTS artists (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    metadata_status TEXT DEFAULT 'pending' -- 'pending', 'complete', 'partial'
);
-- Album data from directories
-- foreign key one(artist) to many(albums)
CREATE TABLE IF NOT EXISTS albums (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    release_year INTEGER,
    path TEXT NOT NULL UNIQUE,
    metadata_status TEXT DEFAULT 'pending', -- 'pending', 'complete', 'partial'
    artist_id INTEGER NOT NULL,
    FOREIGN KEY (artist_id) REFERENCES artists(id)
);
-- Track data from files
-- foreign key one(album) to many(tracks)
CREATE TABLE IF NOT EXISTS tracks (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    duration INTEGER,
    fingerprint TEXT UNIQUE NOT NULL,
    album_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums(id)
);
-- Genres in tree structure
-- self-referencing foreign key for parent genre
CREATE TABLE IF NOT EXISTS genres (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER, -- reference to the parent genre (NULL for main genres)
    UNIQUE(name, parent_id), -- genres can appartain to different parents (Post-Punk)
    FOREIGN KEY (parent_id) REFERENCES genres(id) 
        ON DELETE SET NULL
);
-- Sources of metadata
CREATE TABLE IF NOT EXISTS sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    url TEXT UNIQUE
);

-- Metadata search tasks for albums manager
CREATE TABLE IF NOT EXISTS album_metadata_tasks (
    id INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'done', 'error'
    last_attempt TIMESTAMP,
    album_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE (album_id, source_id),
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
-- Metadata search tasks for artist manager
CREATE TABLE IF NOT EXISTS artist_metadata_tasks (
    id INTEGER PRIMARY KEY,
    status TEXT DEFAULT 'pending', -- 'pending', 'in_progress', 'done', 'error'
    last_attempt TIMESTAMP,
    artist_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE (artist_id, source_id),
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

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
    updated_at TIMESTAMP,
    artist_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE (artist_id, source_id),
    FOREIGN KEY (artist_id) REFERENCES artists(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
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
    length REAL,
    media_links TEXT,
    site_url TEXT,
    cover_url TEXT,
    updated_at TIMESTAMP,
    album_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE (album_id, source_id),
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
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
    updated_at TIMESTAMP,
    track_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    UNIQUE (track_id, source_id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Many-to-many relationship between genres, artists-albums-tracks and sources from metadata
-- role can be 'unspecified', 'main', 'secondary', 'style', 'influence' (non primary key to avoid multiple roles for the same genre from a source)
CREATE TABLE IF NOT EXISTS artist_genres_metadata (
    artist_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    role TEXT DEFAULT 'unspecified',
    PRIMARY KEY (artist_id, genre_id, source_id)
);
CREATE TABLE IF NOT EXISTS album_genres_metadata (
    album_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    role TEXT DEFAULT 'unspecified',
    PRIMARY KEY (album_id, genre_id, source_id),
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);
CREATE TABLE IF NOT EXISTS track_genres_metadata (
    track_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    source_id INTEGER NOT NULL,
    PRIMARY KEY (track_id, genre_id, source_id),
    FOREIGN KEY (track_id) REFERENCES tracks(id),
    FOREIGN KEY (genre_id) REFERENCES genres(id),
    FOREIGN KEY (source_id) REFERENCES sources(id)
);

-- Final metadata for tags 
CREATE TABLE IF NOT EXISTS final_artists_metadata(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    country TEXT,
    metadata_status TEXT
);
CREATE TABLE IF NOT EXISTS final_albums_metadata(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    year INTEGER,
    genres TEXT,
    styles TEXT,
    metadata_status TEXT,
    album_artist_id INTEGER NOT NULL,
    FOREIGN KEY (album_artist_id) REFERENCES artists(id)
);
CREATE TABLE IF NOT EXISTS final_tracks_metadata(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL UNIQUE,
    track_number INTEGER,
    metadata_status TEXT,
    album_id INTEGER NOT NULL,
    track_artist_id INTEGER NOT NULL,
    FOREIGN KEY (album_id) REFERENCES albums(id),
    FOREIGN KEY (track_artist_id) REFERENCES artists(id)
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

