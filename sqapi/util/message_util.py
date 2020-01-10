import json
import logging

MSG_FIELDS = {
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'data_type': {'key': 'data_type', 'required': False},
    'metadata': {'key': 'metadata', 'required': False},
}

log = logging.getLogger(__name__)


def parse_message(message, cfg):
    parser = cfg.get('parser', '')

    if parser.lower() == 'str' or parser.lower() == 'string':
        return parse_string(cfg, message.decode('utf-8'))

    elif parser.lower() == 'json':
        return json.loads(message)

    else:
        err = f'Parser ({parser}) not implemented' if parser else 'Parser not defined'
        log.warning(err)

        raise NotImplementedError(err)


def parse_string(cfg, message):
    fmt = cfg.get('format')
    delimiter = cfg.get('delimiter')

    keys = fmt.split(delimiter)
    values = message.split(delimiter)

    return dict(
        (k, v) for k, v in
        list(zip(keys, values))
    )


def convert_to_internal(message, fields):
    log.debug('Validating required fields of set: {}'.format(fields))
    _validate_required_fields(message, fields)

    return {
        key: message.get(fields.get(key).get('key').lower())
        for key in fields
    }


def _validate_required_fields(message, fields):
    required_fields = {
        fields.get(f).get('key').lower() for f in fields
        if fields.get(f).get('required')
    }

    missing_fields = []

    for f in required_fields:
        if f not in {i.lower() for i in message.keys()}:
            log.debug('Field {} is missing'.format(f))
            missing_fields.append(f)

    if missing_fields:
        err = 'The field(/s) {} are missing in the message'.format(', '.join(missing_fields))
        log.debug(err)
        raise AttributeError(err)
