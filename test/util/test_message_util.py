import hashlib
import uuid
from unittest import TestCase

from sqapi.util import message_util

config = dict({
    # String parsing specific config
    'format': 'uuid.hash.sys.mod.metadata',
    'delimiter': '|',

    # General config
    'message_fields': {
        'uuid': {
            'key': 'uuid',
            'required': True
        },
        'data_location': {
            'key': 'hash',
            'required': True
        },
        'meta_location': {
            'key': 'uuid',
            'required': True
        },
        'metadata': {
            'key': 'metadata',
            'required': False
        },
    },
})


class TestParseMessage(TestCase):
    def setUp(self):
        self.msg_uuid = msg_uuid = str(uuid.uuid4())
        self.msg_hash = msg_hash = hashlib.sha256(self.msg_uuid.encode('UTF-8')).hexdigest()
        self.msg_sys = msg_sys = 'sqapi'
        self.msg_mod = msg_mod = 'test'

        self.json_bytes = f'{"uuid":{msg_uuid},"hash":{msg_hash},"system":{msg_sys},"module":{msg_mod}}'.encode('UTF-8')
        self.string_bytes = f'{msg_uuid}|{msg_hash}|{msg_sys}|{msg_mod}'.encode('UTF-8')

    def TestShould_parse_string(self):
        # Setup
        updated_config = {'parser': 'string'}
        updated_config.update(config)

        # Execute
        result = message_util.parse_message(self.string_bytes, updated_config)

        # Verify
        self.assertEqual(self.msg_uuid, result.get('uuid'))
        self.assertEqual(self.msg_hash, result.get('hash'))
        self.assertEqual(self.msg_sys, result.get('system'))
        self.assertEqual(self.msg_mod, result.get('module'))

    def testShould_parse_json(self):
        # Setup
        updated_config = {'parser': 'json'}
        updated_config.update(config)

        # Execute
        result = message_util.parse_message(self.string_bytes, updated_config)

        # Verify
        self.assertEqual(self.msg_uuid, result.get('uuid'))
        self.assertEqual(self.msg_hash, result.get('hash'))
        self.assertEqual(self.msg_sys, result.get('system'))
        self.assertEqual(self.msg_mod, result.get('module'))

    def test_should_not_parse_due_missing_config(self):
        # Setup
        updated_config = {}
        updated_config.update(config)

        # Execute
        pass

        # Verify
        pass

    def tearDown(self):
        pass


class TestConvertToInternal(TestCase):
    def setUp(self):
        pass

    def test_a(self):
        pass

    def test_b(self):
        pass

    def test_c(self):
        pass

    def tearDown(self):
        pass
