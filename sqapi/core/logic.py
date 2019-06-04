#! /usr/bin/env python3
import os
from datetime import datetime

SQL_SCRIPT_DIR = './db/pg_script/custom'
INSERT_ITEM = 'insert_item.sql'


def execute_logic(config: dict, database, message: dict, metadata: dict, data: bytes):
    """
    This is the custom logic, where all data are available through the parameters.
    Create a structured data set and store it in the database, on disk or what ever you want.

    :param config: util.cfg_util.Config containing the systems configuration.
                    Access the dictionary through config.cfg(key, default)
    :param database: The database connection selected through configuration. Eg. db.postgres.Postgres
                        Available methods
                        <br/>* database.execute_script(script_path, **kwargs)
                        <br/>* database.execute_query(query_string, **kwargs)
                        <br/>* database.update_message(message, status_string)
    :param message: Message as a dictionary, received from message broker. Structure defined in configuration
    :param metadata: Metadata as a dictionary, fields are defined by metadata store and the loader/processor
    :param data: Binary file available as bytes. Be careful not to read large objects into memory :)
    """
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
