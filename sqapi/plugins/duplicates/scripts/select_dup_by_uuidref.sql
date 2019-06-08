-- Select values based on uuid_ref
SELECT *
FROM duplicates
WHERE uuid_ref = %(uuid_ref)s
