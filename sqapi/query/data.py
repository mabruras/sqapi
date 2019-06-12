#! /usr/bin/env python3
import io

from connectors import openstack_swift


def fetch_data(config, message):
    loc = message.get('data_location', None)
    if not loc:
        raise AttributeError('Could not find "data_location" in message')

    try:
        # TODO: More generic selection of metadata store?
        data_store = config.data_store.get('type', 'disk')
        if not data_store or data_store.lower() == 'disk':
            print('Disk (default) was detected as data store')
            return fetch_file_from_disk(loc)

        elif data_store.lower() == 'swift':
            print('OpenStack Swift was detected as data store')
            disk_loc = openstack_swift.download_to_disk(config, loc)
            return fetch_file_from_disk(disk_loc)

        else:
            print('{} is not a supported data store'.format(type))
            return io.BytesIO(bytes())
    except FileNotFoundError as e:
        raise LookupError('Data by reference {} was not available at this moment: {}'.format(loc, str(e)))


def fetch_file_from_disk(file):
    return open(file, "rb")
