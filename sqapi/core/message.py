import uuid


class Message:

    def __init__(self, body: dict, config: dict):
        self.body = body

        self.msg_fields = config.get('message_fields', {})

        self.id = str(uuid.uuid4())
        self.uuid = body.get(self._field_key('uuid'))
        self.type = body.get(self._field_key('type'))
        self.metadata = body.get(self._field_key('metadata'))
        self.data_location = body.get(self._field_key('data_location'))
        self.meta_location = body.get(self._field_key('meta_location'))

    def _field_key(self, field_name: str):
        field = self.msg_fields.get(field_name) or {}

        return field.get('key') or field_name
