-- Inserting values into custom table
INSERT INTO duplicates (
  uuid_ref,
  meta_location,
  data_location,
  sha_256
) VALUES (
  %(uuid_ref)s,
  %(meta_location)s,
  %(data_location)s,
  %(sha_256)s
)
