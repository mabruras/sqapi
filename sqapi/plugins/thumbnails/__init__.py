import io
import logging
import os
import pathlib
from datetime import datetime

from PIL import Image

SQL_SCRIPT_DIR = '{}/scripts'.format(os.path.dirname(__file__))
INSERT_ITEM = 'insert_item.sql'

log = logging.getLogger(__name__)


def execute(config, database, message: dict, metadata: dict, data: io.BufferedReader):
    loc = create_thumbnail(config, message, data)

    save_to_db(database, message, metadata, loc)


def create_thumbnail(config, message, data):
    width = config.custom.get('thumb_size', {}).get('width', 128)
    height = config.custom.get('thumb_size', {}).get('height', 128)
    log.debug('Creating thumbnail with width/height: {}/{}'.format(width, height))

    out = config.custom.get('thumb_dir')

    pathlib.Path(out).mkdir(parents=True, exist_ok=True)

    try:
        im = Image.open(data)
        im.thumbnail((width, height))
        thumb_location = '{}'.format(os.sep).join([out, message.get('uuid_ref')])
        log.debug('Thumbnail is stored in {}'.format(thumb_location))

        im.save(thumb_location, im.format)

        return thumb_location
    except IOError as e:
        err = 'Cannot create thumbnail for {}: {}'.format(data, str(e))
        log.warning(err)
        raise Exception(err)


def save_to_db(database, message, metadata, location):
    log.info('Storing thumbnail reference in database')
    # This defines the kwargs that are sent in as parameters to the SQL script
    output = {
        'uuid_ref': message.get('uuid_ref', None),
        'received_date': message.get('created_at', datetime.now()),
        'meta_location': message.get('meta_location', None),
        'data_location': message.get('data_location', None),
        'mime_type': metadata.get('mime.type', None),
        'thumb_location': location,
    }
    log.debug(output)

    # Resolve path to the script intended to run, to insert your data structure into the database
    script = os.path.join(SQL_SCRIPT_DIR, INSERT_ITEM)

    database.execute_script(script, **output)
