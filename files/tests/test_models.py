import uuid
from django.test import TestCase
from unittest.mock import Mock
from django.contrib.auth import get_user_model
from ..models import user_file_path

User = get_user_model()

class UserFilePathTests(TestCase):

    def setUp(self):
        self.mock_instance = Mock()
        self.mock_instance.owner.id = 1

    def test_standard_file_extension(self):
        path = user_file_path(self.mock_instance, 'test1.txt')
        self.assertTrue(path.startswith("user_1/"))
        self.assertTrue(path.endswith(".txt"))

        # verify filename renamed to a uuid
        filename = path.split("/")[1].replace(".txt", '')
        uuid.UUID(filename)

    def test_file_with_no_extension(self):
        path = user_file_path(self.mock_instance, 'test1')
        self.assertTrue(path.startswith('user_1/'))
        self.assertFalse(path.endswith('.'))  # path should not end with a dot

    def test_file_with_multiple_dots(self):
        path = user_file_path(self.mock_instance, 'archive.tar.gz')
        self.assertTrue(path.endswith('.gz'))
