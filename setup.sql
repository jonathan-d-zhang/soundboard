PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS sound (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    custom_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    size INTEGER NOT NULL,
    added_by TEXT NOT NULL,
    message_id TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sound_filename ON sound (filename);
