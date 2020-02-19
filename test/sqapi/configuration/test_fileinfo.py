from unittest import TestCase
from unittest.mock import patch, Mock

from sqapi.configuration import fileinfo


class TestMimeFromMetadata(TestCase):

    def test_should_find_mime_from_root_level_key(self):
        meta = dict({
            'mime.type': 'application/json',
        })
        config = dict({
            'mime': {
                'path': 'mime.type',
                'path_separator': '-',
            }
        })

        result = fileinfo.mime_from_metadata(meta, config)

        self.assertEqual('application/json', result)

    def test_should_find_mime_once_nested_key(self):
        meta = dict({'wrapper': {
            'mime.type': 'image/jpeg',
        }})

        config = dict({'mime': {
            'path': 'wrapper-mime.type',
            'path_separator': '-',
        }})

        result = fileinfo.mime_from_metadata(meta, config)

        self.assertEqual('image/jpeg', result)

    def test_should_find_mime_multi_nested_key(self):
        meta = dict({'wrapper1': {'wrapper2': {'wrapper3': {
            'mime.type': 'text/plain',
        }}}})

        config = dict({'mime': {
            'path': 'wrapper1-wrapper2-wrapper3-mime.type',
            'path_separator': '-',
        }})

        result = fileinfo.mime_from_metadata(meta, config)

        self.assertEqual('text/plain', result)
        pass

    def test_should_not_find_mime_if_key_does_not_exist(self):
        meta = dict({'wrapper.x': {
            'mime.type': 'image/jpeg',
        }})

        config = dict({'mime': {
            'path': 'wrapper.y_mime.type',
            'path_separator': '-',
        }})

        result = fileinfo.mime_from_metadata(meta, config)

        self.assertIsNone(result)

    def test_should_not_find_mime_due_missing_configuration(self):
        meta = dict({'wrapper': {
            'mime.type': 'image/jpeg',
        }})

        result = fileinfo.mime_from_metadata(meta, dict())

        self.assertIsNone(result)


class TestGuessMimeType(TestCase):
    def setUp(self):
        self.content = b'{"my_key": "my_value"}'
        self.expected_mime = 'application/json'

    @patch('mimetypes.guess_type')
    @patch('filetype.guess')
    def test_should_guess_by_content(self, filetype_mock, mimetypes_mock):
        guessed_filetype_mock = Mock()
        guessed_filetype_mock.mime = self.expected_mime

        filetype_mock.return_value = guessed_filetype_mock

        result = fileinfo.guess_mime_type(self.content)

        self.assertEqual(self.expected_mime, result)
        mimetypes_mock.assert_not_called()
        filetype_mock.assert_called_once_with(self.content)

    @patch('mimetypes.guess_type')
    @patch('filetype.guess')
    def test_should_guess_by_extension(self, filetype_mock, mimetypes_mock):
        filetype_mock.return_value = None
        mimetypes_mock.return_value = (self.expected_mime, None)

        result = fileinfo.guess_mime_type(self.content)

        self.assertEqual(self.expected_mime, result)
        mimetypes_mock.assert_called_once_with(self.content)
        filetype_mock.assert_called_once_with(self.content)

    @patch('mimetypes.guess_type')
    @patch('filetype.guess')
    def test_should_not_guess(self, filetype_mock, mimetypes_mock):
        filetype_mock.return_value = None
        mimetypes_mock.return_value = (None, None)

        result = fileinfo.guess_mime_type(self.content)

        self.assertEqual(None, result)
        mimetypes_mock.assert_called_once_with(self.content)
        filetype_mock.assert_called_once_with(self.content)


class TestValidateMimeType(TestCase):
    def setUp(self):
        self.accepted_types = {
            'image/png',
            'image/jpeg',
            'application/xml',
            'application/json',
        }

    def test_should_have_valid_mime(self):
        mime = 'application/json'

        try:
            fileinfo.validate_mime_type(mime, self.accepted_types)

        except Exception as e:
            self.fail('Should not have thrown exception: {}'.format(str(e)))

    def test_should_not_have_valid_mime(self):
        mime = 'text/plain'

        try:
            fileinfo.validate_mime_type(mime, self.accepted_types)
            self.fail('Should have thrown NotImplementedError')

        except Exception as e:
            self.assertIsInstance(e, NotImplementedError)

    def test_should_be_valid_due_wildcard(self):
        mime = 'audio/mpeg'
        self.accepted_types.update('*')

        try:
            fileinfo.validate_mime_type(mime, self.accepted_types)

        except Exception as e:
            self.fail('Should not have thrown exception: {}'.format(str(e)))

    def tearDown(self):
        # Resetting accepted types
        self.accepted_types = {
            'image/png',
            'image/jpeg',
            'application/xml',
            'application/json',
        }
