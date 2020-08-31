import uuid

from configuration.broker import RabbitMQConfig

from messaging.brokers import Broker
from start import SqapiConfiguration

MSG_FIELDS = {
    'uuid_ref': {'key': 'uuid_ref', 'required': True},
    'data_location': {'key': 'data_location', 'required': True},
    'meta_location': {'key': 'meta_location', 'required': True},
    'data_type': {'key': 'data_type', 'required': False},
    'metadata': {'key': 'metadata', 'required': False},
}


class Message:

    def __init__(self, body: dict):
        self.body = body
        self.config = SqapiConfiguration.MessageConfig()  # Load Configuration
        self.broker = Broker()  # TODO: Load broker (from config?)


class HearBeatMessage(Message):
    def __init__(self, body):
        super().__init__(body)


class InternalMessage(Message):
    def __init__(self, body):
        super().__init__(body)

    def _field_key(self, field_name: str):
        field = self.msg_fields.get(field_name) or {}

        return field.get('key') or field_name


class ExternalMessage(Message):
    def __init__(self, body):
        super().__init__(body)

        self.msg_fields = super().config.get('fields', MSG_FIELDS)
        self.msg_fields.get('data_location').update({'required': True})  # Enforce requirement of data location

        self.hash_digest = None

        self.id = str(uuid.uuid4())
        self.uuid = body.get(self._field_key('uuid'))
        self.type = body.get(self._field_key('type'))
        self.metadata = body.get(self._field_key('metadata'))
        self.data_location = body.get(self._field_key('data_location'))
        self.meta_location = body.get(self._field_key('meta_location'))


if __name__ == '__main__':
    x = RabbitMQConfig()
