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
            auth_version=config.data_store.get('auth_version'),
            os_options=config.data_store.get('os_options') or dict(),
            authurl=config.data_store.get('auth_url', 'http://localhost:8080/auth/v1.0'),
            insecure=True if (config.data_store.get('insecure') or 'false').lower() == 'true' else False,
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
    containers = config.data_store.get('containers')
    if not containers:
        log.debug('No container defined in config, searching all containers available')
        containers = connection.get_account()[-1]

    for c in containers:
        log.debug('Looking for object {} in container {}'.format(object_ref, c.get('name')))
        res = _get_object_from_container(connection, c.get('name'), object_ref)

        if res:
            log.debug('Found object {} in container {}'.format(object_ref, c.get('name')))
            return res

        log.debug('Could not find object {} in container {}'.format(object_ref, c.get('name')))


def _get_object_from_container(connection, container, object_ref):
    try:
        return connection.get_object(container, object_ref)
    except swiftclient.ClientException as e:
        log.debug('Failed while getting object {} from container {}: {}'.format(object_ref, container, str(e)))
