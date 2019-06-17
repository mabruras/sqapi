-- Create your own database initialization here
CREATE TABLE IF NOT EXISTS sizes (
  uuid_ref      TEXT NOT NULL PRIMARY KEY,
  meta_location TEXT,
  data_location TEXT,
  metadata_size INTEGER,
  data_size     INTEGER,
  created_at    TIMESTAMPTZ DEFAULT Now(),
  updated_at    TIMESTAMPTZ DEFAULT Now()
);
