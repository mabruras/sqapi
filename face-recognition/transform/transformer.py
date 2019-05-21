#! /usr/bin/env python
import json


def get_message_transformer(configuration: dict):
    callback = configuration.get('transformer', None)

    if not callback:
        print('Using default message transformer')
        return default_transformer

    return callback


def default_transformer(ch, method, properties, body):
    print('Received channel: {}'.format(ch))
    print('Received method: {}'.format(method))
    print('Received properties: {}'.format(properties))
    print('Received message: {}'.format(body))

    try:
        return json.loads(body)
    except Exception as e:
        print('Could not parse message body to dictionary, returning empty')
        print(body)
        print(e)
        return {}
