-- Create Messages table
CREATE TABLE IF NOT EXISTS messages (
    uuid_ref TEXT NOT NULL PRIMARY KEY,
    meta_location TEXT,
    data_location TEXT,
    data_type TEXT,
    status TEXT
);