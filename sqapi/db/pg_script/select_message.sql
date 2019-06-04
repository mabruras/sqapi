-- Select Message by UUID
SELECT * FROM messages
  WHERE uuid_ref=%(uuid_ref)s;
