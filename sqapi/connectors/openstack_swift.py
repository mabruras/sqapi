#! /usr/bin/env python3
import logging
import os
import tempfile

import swiftclient

log = logging.getLogger(__name__)


def download_to_disk(config, object_ref):
    log.debug('Establishing connection to OpenStack Swift')
    try:
        connection = swiftclient.Connection(
            user=config.data_store.get('access_key_id'),
            key=config.data_store.get('secret_access_key'),
            authurl=config.data_store.get('auth_url', 'http://localhost:8080/auth/v1.0'),
        )
    except Exception as e:
        err = 'Failed establish connection with OpenStack Swift: {}'.format(str(e))
        log.warning(err)
        raise type(e)(err)

    res = _search_containers_for_object(config, connection, object_ref)
    if not res:
        err = 'Could not get object from either containers'
        log.warning(err)
        raise FileNotFoundError(err)

    log.debug('Creating temporary file for Swift object download')
    fd, path = tempfile.mkstemp()
    os.write(fd, res[1])
    os.close(fd)

    return path


def _search_containers_for_object(config, connection, object_ref):
    container = config.data_store.get('container')
    if not container:
        log.debug('No container defined in config, searching all containers avilable')
        # Search for object in all containers
        for c in connection.get_account()[-1]:
            log.debug('Looking for object {} in container {}'.format(object_ref, c.get('name')))
            res = _get_object_from_container(connection, c.get('name'), object_ref)
            if res:
                log.debug('Found object {} in container {}'.format(object_ref, c.get('name')))
                return res
            log.warning('Could not find object {} in container {}'.format(object_ref, c.get('name')))
    else:
        return _get_object_from_container(connection, container, object_ref)


def _get_object_from_container(connection, container, object_ref):
    try:
        return connection.get_object(container, object_ref)
    except swiftclient.ClientException as e:
        err = 'Failed while getting object {} from container {}: {}'.format(object_ref, container, str(e))
        log.warning(err)
        raise FileNotFoundError(err)
