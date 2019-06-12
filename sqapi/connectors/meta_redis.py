#! /usr/bin/env python3
import redis


def fetch_metadata_as_dict(config, reference):
    host = config.meta_store.get('host', 'localhost')
    port = config.meta_store.get('port', 6379)
    r = redis.Redis(host=host, port=port)

    res = r.get(reference)

    if not res:
        raise LookupError('Metadata by reference "{}" was not available at this moment'.format(reference))

    return res
