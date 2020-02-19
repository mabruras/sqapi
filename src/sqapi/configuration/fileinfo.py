import logging
import mimetypes

import filetype

APPLICATION_OCTET_STREAM = 'application/octet-stream'

log = logging.getLogger(__name__)


def get_mime_type(data_path, metadata, config):
    return mime_from_metadata(metadata, config) or guess_mime_type(data_path) or APPLICATION_OCTET_STREAM


def mime_from_metadata(metadata, config):
    mime = config.get('mime')
    if not mime:
        return None

    mime_path = mime.get('path', '')
    mime_separator = mime.get('path_separator', '.')

    val = metadata
    for key in mime_path.split(mime_separator):
        val = val.get(key, {})

    return val or None


def guess_mime_type(file_path):
    log.info('Guessing mime type')

    guessed_type = filetype.guess(file_path)
    if guessed_type:
        return guessed_type.mime

    guessed_type = mimetypes.guess_type(file_path)
    if guessed_type[0]:
        return guessed_type[0]


def validate_mime_type(mime, accepted_types):
    log.debug('Validating mime type')
    log.debug('Accepted mime types: {}'.format(accepted_types))

    if accepted_types and (
            mime not in accepted_types
            and '*' not in accepted_types
    ):
        err = 'Mime type "{}" is not supported by any of the active sqAPI plugins'.format(mime)
        log.debug(err)
        raise NotImplementedError(err)
