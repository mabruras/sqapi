-- Insert Message
INSERT INTO messages (
  uuid,
  meta_location,
  data_location,
  data_type,
  status
)
VALUES (
  %(uuid)s,
  %(meta_location)s,
  %(data_location)s,
  %(data_type)s,
  %(status)s
);
