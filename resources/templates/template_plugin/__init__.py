import io
import logging
import os

from sqapi.core.message import Message

SQL_SCRIPT_DIR = '{}/scripts'.format(os.path.dirname(__file__))
INSERT_ITEM = 'insert_item.sql'

"""
Using default Python logging framework
"""
log = logging.getLogger(__name__)


def execute(config, database, message: Message, metadata: dict, data: io.BufferedReader):
    """
    This is the custom logic, where all data are available through the parameters.
    Create a structured data set and store it in the database, on disk or what ever you want.

    It should always be considered extracting logic into separate functions,
    to keep the execute function as readable as possible.

    **NOTICE**: This function (execute) is the ONLY required function of this module.

    :param config: util.cfg_util.Config containing the systems configuration.
                    Access the dictionary through config.cfg(key, default)
    :param database: The database connection selected through configuration. Eg. db.postgres.Postgres
                        Available methods
                        <br/>× database.execute_script(script_path, **kwargs)
                        <br/>× database.execute_query(query_string, **kwargs)
                        <br/>× database.update_message(message, status_string)
    :param message: Message as a dictionary, received from message broker. Structure defined in configuration
    :param metadata: Metadata as a dictionary, fields are defined by metadata store and the loader/processor
    :param data: Binary file available through a BufferedReader. Be careful not to read large objects into memory :)
    """
    log.info('Getting metadata count and size of data payload')
    sizes = get_sizes(metadata, data)
    out = convert_to_db_insert(message, *sizes)
    save_to_db(database, out)


def get_sizes(metadata, data):
    """
    Get size is this templates core logic, but there is not restrictions for what could or should be done :)

    :param metadata: Metadata received from sqAPI
    :param data: Data content received from sqAPI
    :return: Tuple containing length of metadata and size of data payload
    """
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
    """
    This defines the kwargs that are sent in as parameters to the SQL script.

    :param message: Message received from sqAPI
    :param meta_size: Calculated length of metadata
    :param data_size: Calculated size of data payload
    :return: dictionary prepared for database script
    """
    return {
        'uuid_ref': message.uuid,
        'meta_location': message.meta_location,
        'data_location': message.data_location,
        'metadata_size': meta_size,
        'data_size': data_size,
    }


def save_to_db(database, output):
    log.info('Storing sizes in database')
    log.debug(output)

    # Resolve path to the script intended to run,
    # to insert your data structure into the database
    script = os.path.join(SQL_SCRIPT_DIR, INSERT_ITEM)
    database.execute_script(script, **output)
