import hashlib
import json
import logging
import uuid

MSG_FIELDS = {
    'data_type': {'key': 'data_type', 'required': False},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'metadata': {'key': 'metadata', 'required': False},
}

log = logging.getLogger(__name__)


def parse_message(message, config):
    parser = config.get('parser', '')

    if parser.lower() == 'str' or parser.lower() == 'string':
        return parse_string(config, message.decode('utf-8'))

    elif parser.lower() == 'json':
        return json.loads(message)

    else:
        err = f'Parser ({parser}) not implemented' if parser else 'Parser not defined'
        log.warning(err)

        raise NotImplementedError(err)


def parse_string(config, message):
    fmt = config.get('format')
    delimiter = config.get('delimiter')

    keys = fmt.split(delimiter)
    values = message.split(delimiter)

    return dict(
        (k, v) for k, v in
        list(zip(keys, values))
    )


def validate_message(message, req_fields):
    log.debug('Validating required fields of set: {}'.format(req_fields))
    required_fields = {
        req_fields.get(f).get('key').lower() for f in req_fields
        if req_fields.get(f).get('required')
    }
    log.debug('Required fields: {}'.format(required_fields))
    missing_fields = []

    for f in required_fields:
        if f not in {i.lower() for i in message.keys()}:
            log.debug('Field {} is missing'.format(f))
            missing_fields.append(f)

    if missing_fields:
        err = 'The field(/s) {} are missing in the message'.format(', '.join(missing_fields))
        log.debug(err)
        raise AttributeError(err)

    return message


if __name__ == '__main__':
    config = {
        'parser': 'str',
        'delimiter': '.',
        'format': 'uuid_ref.data_location.meta_location.metadata',
    }

    uuid_ref = str(uuid.uuid4())
    hash_ref = hashlib.sha256(b'').hexdigest()
    meta = {}

    msg = f'{uuid_ref}.{hash_ref}.{uuid_ref}.{json.dumps(meta)}'

    res = parse_message(msg.encode('utf-8'), config)
    print(res)
