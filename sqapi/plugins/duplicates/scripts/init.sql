-- Create your own database initialization here
CREATE TABLE IF NOT EXISTS duplicates (
  uuid_ref      TEXT NOT NULL PRIMARY KEY,
  meta_location TEXT,
  data_location TEXT,
  sha_256       TEXT,
  created_at    TIMESTAMPTZ DEFAULT Now(),
  updated_at    TIMESTAMPTZ DEFAULT Now()
);
