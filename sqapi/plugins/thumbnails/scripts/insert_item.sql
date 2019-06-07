-- Inserting values into custom table
INSERT INTO items (
  uuid_ref,
  received_date,
  meta_location,
  data_location,
  mime_type,
  file_size
) VALUES (
  %(uuid_ref)s,
  %(received_date)s,
  %(meta_location)s,
  %(data_location)s,
  %(mime_type)s,
  %(file_size)s
)
