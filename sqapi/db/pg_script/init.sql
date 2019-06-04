-- Create your own database initialization here
CREATE TABLE IF NOT EXISTS items (
    uuid_ref TEXT NOT NULL PRIMARY KEY,
    meta_location TEXT,
    data_location TEXT,
    mime_type TEXT,
    file_size INTEGER,
    received_date TIMESTAMPTZ DEFAULT Now(),
    created_at TIMESTAMPTZ DEFAULT Now(),
    updated_at TIMESTAMPTZ DEFAULT Now()
);
