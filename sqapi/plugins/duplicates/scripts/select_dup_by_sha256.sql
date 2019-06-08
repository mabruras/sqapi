-- Select values based on uuid_ref
SELECT *
FROM duplicates
WHERE sha_256 = %(sha_256)s
