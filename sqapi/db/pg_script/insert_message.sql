-- Insert Message
INSERT INTO messages (
  id,
  uuid_ref,
  meta_location,
  data_location,
  data_type,
  status
)
VALUES (
  %(id)s,
  %(uuid_ref)s,
  %(meta_location)s,
  %(data_location)s,
  %(data_type)s,
  %(status)s
);
