-- Create tables for storing story generation data
CREATE TABLE IF NOT EXISTS stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    system_prompt TEXT,
    style TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mode TEXT,
    memory_added BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(filename, file_hash)
);

CREATE TABLE IF NOT EXISTS story_documents (
    story_id INTEGER,
    document_id INTEGER,
    FOREIGN KEY (story_id) REFERENCES stories(id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    PRIMARY KEY (story_id, document_id)
); 