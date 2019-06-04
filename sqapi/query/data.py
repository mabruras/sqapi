#! /usr/bin/env python3
import io


def fetch_data(config, message):
    loc = message.get('data_location', None)
    if not loc:
        raise AttributeError('Could not find "data_location" in message')

    # TODO: More generic selection of metadata store?
    data_store = config.cfg_data('type', 'disk')
    if not data_store:
        print('Using default data store: disk')
        disk_loc = fetch_data_to_disk(loc)
        return fetch_file_from_disk(disk_loc)

    elif data_store.lower() == 'disk':
        print('Disk was detected as data store')
        disk_loc = fetch_data_to_disk(loc)
        try:
            return fetch_file_from_disk(disk_loc)
        except FileNotFoundError as e:
            raise LookupError('Data by reference {} was not available at this moment'.format(loc))

    else:
        print('{} is not a supported data store'.format(type))
        return io.BytesIO(bytes())


def fetch_data_to_disk(location):
    # TODO: this return should be from a specific/configurable module
    # so it will download/get file data from all kinds of storage places

    # TODO: Now location is returned since we know in this POC that the file is on disk
    return location


def fetch_file_from_disk(file):
    return open(file, "rb")
