#! /usr/bin/env python3
import os
import tempfile

import swiftclient


def download_to_disk(config, object_ref):
    try:
        connection = swiftclient.Connection(
            user=config.data_store.get('access_key_id'),
            key=config.data_store.get('secret_access_key'),
            authurl=config.data_store.get('auth_url', 'http://localhost:8080/auth/v1.0'),
        )
    except Exception as e:
        err = 'Failed establish connection with OpenStack Swift: {}'.format(str(e))
        raise type(e)(err)

    res = _search_containers_for_object(config, connection, object_ref)
    if not res:
        err = 'Could not get object from either containers'
        raise FileNotFoundError(err)

    fd, path = tempfile.mkstemp()
    os.write(fd, res[1])
    os.close(fd)

    return path


def _search_containers_for_object(config, connection, object_ref):
    container = config.data_store.get('container')
    if not container:
        # Search for object in all containers
        for c in connection.get_account()[-1]:
            res = _get_object_from_container(connection, c.get('name'), object_ref)
            if res:
                return res
    else:
        return _get_object_from_container(connection, container, object_ref)


def _get_object_from_container(connection, container, object_ref):
    try:
        return connection.get_object(container, object_ref)
    except swiftclient.ClientException as e:
        err = 'Failed while getting object {} from container {}: {}'.format(object_ref, container, str(e))
        raise FileNotFoundError(err)
