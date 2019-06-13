-- Inserting values into custom table
INSERT INTO thumbnails (
  uuid_ref,
  received_date,
  meta_location,
  data_location,
  mime_type,
  thumb_location
) VALUES (
  %(uuid_ref)s,
  %(received_date)s,
  %(meta_location)s,
  %(data_location)s,
  %(mime_type)s,
  %(thumb_location)s
)
