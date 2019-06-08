-- Create Messages table
CREATE TABLE IF NOT EXISTS messages (
  id            TEXT NOT NULL PRIMARY KEY,
  uuid_ref      TEXT NOT NULL,
  meta_location TEXT,
  data_location TEXT,
  data_type     TEXT,
  status        TEXT,
  info          TEXT,
  created_at    TIMESTAMPTZ DEFAULT Now(),
  updated_at    TIMESTAMPTZ DEFAULT Now()
);
