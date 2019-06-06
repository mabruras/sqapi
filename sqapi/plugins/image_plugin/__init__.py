import os
from datetime import datetime

SQL_SCRIPT_DIR = '{}/scripts'.format(os.path.dirname(__file__))
INSERT_ITEM = 'insert_item.sql'


def execute(config, database, message: dict, metadata: dict, data: bytes):
    print('Metadata: {}'.format(metadata))
    print('Data processing started')
    content_size = data.seek(0, 2)
    data.close()
    print('File size: {}'.format(content_size))
    print('Data processing ended')

    # This defines the kwargs that are sent in as parameters to the SQL script
    output = {
        'uuid_ref': message.get('uuid_ref', None),
        'received_date': message.get('created_at', datetime.now()),
        'meta_location': message.get('meta_location', None),
        'data_location': message.get('data_location', None),
        'mime_type': metadata.get('mime.type', None),
        'file_size': content_size,
    }

    # Resolve path to the script intended to run, to insert your data structure into the database
    script = os.path.join(SQL_SCRIPT_DIR, INSERT_ITEM)

    database.execute_script(script, **output)
