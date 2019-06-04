#! /usr/bin/env python3
import json

import redis


def fetch_metadata(config, message):
    loc = message.get('meta_location', None)
    if not loc:
        raise AttributeError('Could not find "data_location" in message')

    # TODO: More generic selection of metadata store?
    # meta_store = config.cfg_meta('type', 'redis')
    meta_store, uuid_ref = loc.split('/')

    if not meta_store:
        # Default Metadata store is Redis
        print('Using default metadata store: Redis')
        out = fetch_meta_from_redis(redis.Redis, config, uuid_ref)
        if not out:
            raise LookupError('Metadata by reference "{}" was not available at this moment'.format(uuid_ref))

        return json.loads(out)

    elif meta_store.lower() == 'redis':
        print('Redis was detected as metadata store')
        out = fetch_meta_from_redis(redis.Redis, config, uuid_ref)
        if not out:
            raise LookupError('Metadata by reference "{}" was not available at this moment'.format(uuid_ref))

        return json.loads(out)
    else:
        print('{} is not a supported metadata store'.format(type))
        return dict()


def fetch_meta_from_redis(clazz, config, reference):
    host = config.cfg_meta('host', 'localhost')
    port = config.cfg_meta('port', 6379)
    r = clazz(host=host, port=port)

    return r.get(reference)
