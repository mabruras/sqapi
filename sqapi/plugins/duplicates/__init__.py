import hashlib
import io
import logging
import os

SQL_SCRIPT_DIR = '{}/scripts'.format(os.path.dirname(__file__))
INSERT_ITEM = 'insert_dup.sql'

log = logging.getLogger(__name__)


def execute(config, database, message: dict, metadata: dict, data: io.BufferedReader):
    sha_256 = calculate_sha256(metadata, data)

    save_to_db(database, message, sha_256)


def calculate_sha256(metadata, data):
    log.info('Calculating SHA-256 of object')
    sha_256 = metadata.get('sha256', None) or metadata.get('sha-256', None) or metadata.get('sha_256', None)

    if not sha_256:
        sha_256 = hashlib.sha256(data.read()).hexdigest()

    log.debug('Hash calculated: {}'.format(sha_256))
    return sha_256


def save_to_db(database, message, sha_256):
    log.info('Storing hash in database')
    # This defines the kwargs that are sent in as parameters to the SQL script
    output = {
        'uuid_ref': message.get('uuid_ref', None),
        'meta_location': message.get('meta_location', None),
        'data_location': message.get('data_location', None),
        'sha_256': sha_256,
    }
    log.debug(output)

    # Resolve path to the script intended to run, to insert your data structure into the database
    script = os.path.join(SQL_SCRIPT_DIR, INSERT_ITEM)

    database.execute_script(script, **output)
