#! /usr/bin/env python3

import redis

r = redis.Redis(host='localhost', port=6379, db=0)

v = r.get('foo')
print(f'value of foo: {v}')
