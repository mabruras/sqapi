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


def parse_message(message: bytes, cfg) -> dict:
    parser = cfg.get('parser', '')

    if parser.lower() == 'str' or parser.lower() == 'string':
        return _parse_string(cfg, message.decode('utf-8'))

    elif parser.lower() == 'json':
        return json.loads(message)

    else:
        err = f'Parser ({parser}) not implemented' if parser else 'Parser not defined'
        log.warning(err)

        raise NotImplementedError(err)


def _parse_string(cfg, message):
    fmt = cfg.get('format')
    delimiter = cfg.get('delimiter')

    keys = fmt.split(delimiter)
    values = message.split(delimiter)

    return dict(
        (k, v) for k, v in
        list(zip(keys, values))
    )
