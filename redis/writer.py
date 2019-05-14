#! /usr/bin/env python3

import redis

r = redis.Redis(host='localhost', port=6379, db=0)

r.set('foo','bar')

