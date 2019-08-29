-- Insert Message
INSERT INTO messages (
  id,
  uuid,
  meta_location,
  data_location,
  data_type,
  status
)
VALUES (
  %(id)s,
  %(uuid)s,
  %(meta_location)s,
  %(data_location)s,
  %(data_type)s,
  %(status)s
);
