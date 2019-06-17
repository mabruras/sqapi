-- Select values based on uuid_ref
SELECT *
FROM sizes
WHERE uuid_ref = %(uuid_ref)s
