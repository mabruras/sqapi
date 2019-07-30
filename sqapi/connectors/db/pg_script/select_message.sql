-- Select Message by UUID
SELECT *
FROM messages
WHERE uuid=%(uuid)s;
