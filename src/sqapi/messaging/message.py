import uuid

MSG_FIELDS = {
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'data_type': {'key': 'data_type', 'required': False},
    'metadata': {'key': 'metadata', 'required': False},
}


class Message:

    def __init__(self, body: dict, config: dict):
        self.body = body

        self.msg_fields = config.get('message_fields', MSG_FIELDS)
        self.msg_fields.get('data_location').update({'required': True})  # Enforce requirement of content location

        self.hash_digest = None

        self.id = str(uuid.uuid4())
        self.uuid = body.get(self._field_key('uuid'))
        self.type = body.get(self._field_key('type'))
        self.metadata = body.get(self._field_key('metadata'))
        self.data_location = body.get(self._field_key('data_location'))
        self.meta_location = body.get(self._field_key('meta_location'))

    def _field_key(self, field_name: str):
        field = self.msg_fields.get(field_name) or {}

        return field.get('key') or field_name

    def __str__(self):
        msg = {
            'id': self.id,
            'uuid': self.uuid,
            'type': self.type,
            'metadata': self.metadata,
            'data_location': self.data_location,
            'meta_location': self.meta_location,
            'hash_digest': self.hash_digest,
        }
        return str(msg)
