#! /usr/bin/env python3
import io
import logging

from sqapi.connectors import openstack_swift

log = logging.getLogger(__name__)


def fetch_data(config, message):
    loc = message.get('data_location', None)
    if not loc:
        err = 'Could not find "data_location" in message'
        log.warning(err)
        raise AttributeError(err)

    try:
        # TODO: More generic selection of metadata store?
        data_store = config.data_store.get('type', 'disk')
        if not data_store or data_store.lower() == 'disk':
            log.info('Disk (default) was detected as data store')
            return fetch_file_from_disk(loc)

        elif data_store.lower() == 'swift':
            log.info('OpenStack Swift was detected as data store')
            disk_loc = openstack_swift.download_to_disk(config, loc)
            return fetch_file_from_disk(disk_loc)

        else:
            log.warning('{} is not a supported data store'.format(type))
            return io.BytesIO(bytes())
    except FileNotFoundError as e:
        err = 'Data by reference {} was not available at this moment: {}'.format(loc, str(e))
        log.warning(err)
        raise LookupError(err)


def fetch_file_from_disk(file):
    return open(file, "rb")
