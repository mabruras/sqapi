-- Inserting values into custom table
INSERT INTO sizes (
  uuid_ref,
  meta_location,
  data_location,
  metadata_size,
  data_size
) VALUES (
  %(uuid_ref)s,
  %(meta_location)s,
  %(data_location)s,
  %(metadata_size)s,
  %(data_size)s
)
