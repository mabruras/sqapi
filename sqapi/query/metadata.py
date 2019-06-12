#! /usr/bin/env python3
import json

from connectors import meta_redis


def fetch_metadata(config, message):
    loc = message.get('meta_location', None)
    if not loc:
        raise AttributeError('Could not find "meta_location" in message')

    # TODO: More generic selection of metadata store?
    # meta_store = config.cfg_meta('type', 'redis')
    meta_store, uuid_ref = loc.split('/')

    if not meta_store or meta_store.lower() == 'redis':
        print('Redis (default) was detected as metadata store')
        out = meta_redis.fetch_metadata_as_dict(config, uuid_ref)

        return json.loads(out)
    else:
        print('{} is not a supported metadata store'.format(type))
        return dict()
