#! /usr/bin/env python3
import json
import logging

from sqapi.connectors.meta import redis

log = logging.getLogger(__name__)


def fetch_metadata(config, message):
    loc = message.get('meta_location', None)
    if not loc:
        err = 'Could not find "meta_location" in message'
        log.warning(err)
        raise AttributeError(err)

    # TODO: More generic selection of metadata store?
    # meta_store = config.cfg_meta('type', 'redis')
    meta_store, uuid_ref = loc.split('/')

    if not meta_store or meta_store.lower() == 'redis':
        log.info('Redis (default) was detected as metadata store')
        out = redis.fetch_metadata_as_dict(config, uuid_ref)

        return json.loads(out)
    else:
        log.warning('{} is not a supported metadata store'.format(type))
        return dict()
