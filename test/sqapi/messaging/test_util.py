import hashlib
import json
import uuid
from unittest import TestCase

from sqapi.messaging import util

config = dict({
    # String parsing specific config
    'format': 'uuid|hash|system|module|metadata',
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

        self.json_bytes = json.dumps({
            'uuid': msg_uuid, 'hash': msg_hash,
            'system': msg_sys, 'module': msg_mod
        }).encode('UTF-8')
        self.string_bytes = '{}|{}|{}|{}'.format(msg_uuid, msg_hash, msg_sys, msg_mod).encode('UTF-8')

    def test_should_parse_string(self):
        # Setup
        updated_config = {'parser': 'string'}
        updated_config.update(config)

        # Execute
        result = util.parse_message(self.string_bytes, updated_config)

        # Verify
        self.assertEqual(self.msg_uuid, result.uuid)
        self.assertEqual(self.msg_uuid, result.meta_location)
        self.assertEqual(self.msg_hash, result.data_location)

        self.assertEqual(self.msg_sys, result.body.get('system'))
        self.assertEqual(self.msg_mod, result.body.get('module'))

    def test_should_parse_json(self):
        # Setup
        updated_config = {'parser': 'json'}
        updated_config.update(config)

        # Execute
        result = util.parse_message(self.json_bytes, updated_config)

        # Verify
        self.assertEqual(self.msg_uuid, result.uuid)
        self.assertEqual(self.msg_uuid, result.meta_location)
        self.assertEqual(self.msg_hash, result.data_location)

        self.assertEqual(self.msg_sys, result.body.get('system'))
        self.assertEqual(self.msg_mod, result.body.get('module'))

    def test_should_not_parse_due_missing_config(self):
        # Setup
        updated_config = {}
        updated_config.update(config)

        # Execute
        try:
            util.parse_message(self.json_bytes, updated_config)
            self.fail("Should have thrown exception due missing parse field in config")
        except Exception as e:
            # Verify
            self.assertTrue(isinstance(e, NotImplementedError))

    def tearDown(self):
        pass
