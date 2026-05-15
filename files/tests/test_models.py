import uuid
from django.test import TestCase
from unittest.mock import Mock
from django.contrib.auth import get_user_model
from ..models import user_file_path, Folder

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


class FolderModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')

    def test_folder_creation(self):
        folder = Folder.objects.create(name="Documents", owner=self.user)
        self.assertEqual(str(folder), "Documents")
        self.assertEqual(folder.owner, self.user)
        self.assertIsNone(folder.parent)

    def test_folder_nesting(self):
        root = Folder.objects.create(name="Root", owner=self.user)
        child = Folder.objects.create(name="Child", parent=root, owner=self.user)
        self.assertEqual(root.subfolders.count(), 1)
        self.assertEqual(root.subfolders.first(), child)
        self.assertEqual(child.parent, root)
