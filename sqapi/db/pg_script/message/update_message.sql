-- Update Message
UPDATE messages SET
  status = %(status)s,
  info = %(info)s,
  updated_at = Now()
WHERE uuid_ref = %(uuid_ref)s;
