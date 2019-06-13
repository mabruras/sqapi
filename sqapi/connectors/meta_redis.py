#! /usr/bin/env python3
import logging

import redis

log = logging.getLogger(__name__)


def fetch_metadata_as_dict(config, reference):
    log.debug('Fetching metadata from Redis')
    host = config.meta_store.get('host', 'localhost')
    port = config.meta_store.get('port', 6379)
    log.debug('Connecting to redis on {}:{}'.format(host, port))
    r = redis.Redis(host=host, port=port)

    res = r.get(reference)

    if not res:
        log.warning('Response from Redis, on key="{}" was empty'.format(reference))
        raise LookupError('Metadata by reference "{}" was not available at this moment'.format(reference))

    return res
