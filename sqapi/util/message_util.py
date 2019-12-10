import logging

MSG_FIELDS = {
    'data_type': {'key': 'data_type', 'required': True},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'metadata': {'key': 'metadata', 'required': False},
}

log = logging.getLogger(__name__)


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
