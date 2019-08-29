-- Select Message by UUID
SELECT *
FROM messages
WHERE id = %(id)s;
