import io
import logging
import os

SQL_SCRIPT_DIR = '{}/scripts'.format(os.path.dirname(__file__))
INSERT_ITEM = 'insert_item.sql'

log = logging.getLogger(__name__)


def execute(config, database, message: dict, metadata: dict, data: io.BufferedReader):
    log.info('Getting metadata count and size of data payload')
    sizes = get_sizes(metadata, data)
    out = convert_to_db_insert(message, *sizes)
    save_to_db(database, out)


def get_sizes(metadata, data):
    log.debug('Getting length of metadata')
    log.debug(metadata)
    metadata_size = len(metadata)

    log.debug('Getting size of payload')
    log.debug(data.read())
    data_size = data.tell()
    data.close()
    log.debug(data_size)

    return metadata_size, data_size


def convert_to_db_insert(message, meta_size, data_size):
    return {
        'uuid_ref': message.get('uuid_ref', None),
        'meta_location': message.get('meta_location', None),
        'data_location': message.get('data_location', None),
        'metadata_size': meta_size,
        'data_size': data_size,
    }


def save_to_db(database, output):
    log.info('Storing sizes in database')
    log.debug(output)

    script = os.path.join(SQL_SCRIPT_DIR, INSERT_ITEM)
    database.execute_script(script, **output)
