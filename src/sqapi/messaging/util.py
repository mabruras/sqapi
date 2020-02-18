import json
import logging

from sqapi.messaging.message import Message

log = logging.getLogger(__name__)


def parse_message(msg_body: bytes, cfg) -> Message:
    parser = cfg.get('parser', '')

    if parser.lower() == 'str' or parser.lower() == 'string':
        out = _parse_string(cfg, msg_body.decode('utf-8'))

    elif parser.lower() == 'json':
        out = json.loads(msg_body)

    else:
        err = f'Parser ({parser}) not implemented' if parser else 'Parser not defined'
        log.error(err)

        raise NotImplementedError(err)

    message = Message(out, cfg)
    _validate_required_fields(message)

    return message


def _parse_string(cfg, message):
    fmt = cfg.get('format')
    delimiter = cfg.get('delimiter')

    keys = fmt.split(delimiter)
    values = message.split(delimiter)

    return dict(
        (k, v) for k, v in
        list(zip(keys, values))
    )


def _validate_required_fields(message):
    body = message.body
    fields = message.msg_fields

    required_fields = {
        fields.get(f).get('key').lower() for f in fields
        if fields.get(f).get('required')
    }

    missing_fields = [
        f for f in required_fields
        if f not in {
            i.lower() for i in body.keys()
        }
    ]

    if missing_fields:
        err = 'The following field(/s) are missing in the message: {}'.format(', '.join(missing_fields))
        log.debug(err)
        raise AttributeError(err)


def extract_mime_from_metadata(config, metadata):
    # TODO: Check path of mime-type from config
    # TODO: Extract mime-type from metadata if possible or return null
    pass
