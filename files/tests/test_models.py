import uuid
from django.test import TestCase
from unittest.mock import Mock
from django.contrib.auth import get_user_model
from ..models import user_file_path, Folder, File

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

    def test_total_size_empty_folder(self):
        folder = Folder.objects.create(name="Documents", owner=self.user)
        self.assertEqual(folder.total_size(), 0)

    def test_total_size_with_files(self):
        folder = Folder.objects.create(name="Documents", owner=self.user)
        File.objects.create(name="test1.txt", size=150, folder=folder, owner=self.user)
        File.objects.create(name="test2.txt", size=50, folder=folder, owner=self.user)
        self.assertEqual(folder.total_size(), 200)

    def test_total_size_recursive_with_nested_folders(self):
        root = Folder.objects.create(name="Root", owner=self.user)
        child = Folder.objects.create(name="Child", parent=root, owner=self.user)
        grandchild = Folder.objects.create(name="Grandchild", parent=child, owner=self.user)

        File.objects.create(name="root_file.txt", size=10, folder=root, owner=self.user)
        File.objects.create(name="child_file.txt", size=20, folder=child, owner=self.user)
        File.objects.create(name="grandchild_file.txt", size=30, folder=grandchild, owner=self.user)

        self.assertEqual(grandchild.total_size(), 30)
        self.assertEqual(child.total_size(), 50)  # 20 + 30
        self.assertEqual(root.total_size(), 60)  # 10 + 20 + 30


class FileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.folder = Folder.objects.create(name="Documents", owner=self.user)

    def test_file_creation(self):
        file = File.objects.create(
            file="file_path.txt", name="test.txt", size=25, folder=self.folder, owner=self.user
        )
        self.assertEqual(str(file), "test.txt")
        self.assertEqual(file.folder, self.folder)

    def test_cascade_delete_on_folder(self):
        File.objects.create(
            file="file_path.txt", name="test.txt", size=25, folder=self.folder, owner=self.user
        )
        self.assertEqual(File.objects.count(), 1)
        self.folder.delete()
        self.assertEqual(File.objects.count(), 0)

    def test_cascade_delete_on_user(self):
        File.objects.create(
            file="file_path.txt", name="test.txt", size=25, folder=self.folder, owner=self.user
        )
        self.assertEqual(File.objects.count(), 1)
        self.user.delete()
        self.assertEqual(File.objects.count(), 0)
