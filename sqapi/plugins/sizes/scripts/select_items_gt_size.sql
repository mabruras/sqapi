-- Select values based on uuid_ref
SELECT *
FROM sizes
WHERE data_size > %(data_size)s;
