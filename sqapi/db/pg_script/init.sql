-- Create your own database initialization here
SELECT table_name FROM information_schema.tables
  WHERE table_schema = 'public'
