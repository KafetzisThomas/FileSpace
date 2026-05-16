import os
import io
import zipfile
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import FileResponse
from ..models import Folder, File

User = get_user_model()

class DriveViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user_1 = User.objects.create_user(username='user1', password='password123')
        self.user_2 = User.objects.create_user(username='user2', password='password123')

        self.root_folder_user_1 = Folder.objects.create(name="Root A", owner=self.user_1)
        self.sub_folder_user_1 = Folder.objects.create(name="Sub A", parent=self.root_folder_user_1, owner=self.user_1)
        self.root_file_user_1 = File.objects.create(name="root_file.txt", size=100, owner=self.user_1)
        self.sub_file_user_1 = File.objects.create(name="sub_file.txt", size=100, folder=self.sub_folder_user_1, owner=self.user_1)
        self.folder_user_2 = Folder.objects.create(name="Root B", owner=self.user_2)

        self.url_root = reverse('files:drive')        

    def test_unauthenticated_user_redirects_to_login(self):
        response = self.client.get(self.url_root)
        self.assertRedirects(response, f'/user/login/?next={self.url_root}')

    def test_user_cannot_access_other_users_folder(self):
        self.client.login(username='user1', password='password123')
        url_other_user_folder = reverse('files:drive_folder', kwargs={'folder_id': self.folder_user_2.id})

        response = self.client.get(url_other_user_folder)
        self.assertEqual(response.status_code, 404)

    def test_root_drive_displays_correct_items(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url_root)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context['current_folder'])

        # should only contain root items (parent/folder == None)
        self.assertIn(self.root_folder_user_1, response.context['folders'])
        self.assertNotIn(self.sub_folder_user_1, response.context['folders'])
        self.assertIn(self.root_file_user_1, response.context['files'])
        self.assertEqual(response.context['total_items_count'], 2)

    def test_subfolder_displays_correct_items(self):
        self.client.login(username='user1', password='password123')
        url_subfolder = reverse('files:drive_folder', kwargs={'folder_id': self.root_folder_user_1.id})
        response = self.client.get(url_subfolder)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['current_folder'], self.root_folder_user_1)

        # should contain items inside Root A
        self.assertIn(self.sub_folder_user_1, response.context['folders'])
        self.assertNotIn(self.root_folder_user_1, response.context['folders'])
        self.assertEqual(response.context['total_items_count'], 1)

    def test_search_finds_nested_files(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url_root, {'search': 'sub_file'})
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['search'], 'sub_file')
        self.assertIn(self.sub_file_user_1, response.context['files'])
        self.assertNotIn(self.root_file_user_1, response.context['files'])


class UploadFilesViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.user_1_folder = Folder.objects.create(name="Documents", owner=self.user1)
        self.user_2_folder = Folder.objects.create(name="Projects", owner=self.user2)

        self.url = reverse('files:upload_files')

        self.file1 = SimpleUploadedFile("test1.txt", b"test_content_1")
        self.file2 = SimpleUploadedFile("test2.txt", b"test_content_2")

    def test_get_request_is_rejected(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_redirects_to_login(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/user/login/'))

    def test_upload_to_root_drive(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(self.url, {'file_field': [self.file1, self.file2]})

        self.assertRedirects(response, reverse('files:drive'))
        self.assertEqual(File.objects.filter(owner=self.user1).count(), 2)

        uploaded_file = File.objects.get(name="test1.txt")
        self.assertIsNone(uploaded_file.folder)

    def test_upload_to_specific_folder(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(self.url, {'file_field': [self.file1], 'folder_id': self.user_1_folder.id})

        self.assertRedirects(response, reverse('files:drive_folder', kwargs={'folder_id': self.user_1_folder.id}))

        uploaded_file = File.objects.get(name="test1.txt")
        self.assertEqual(uploaded_file.folder, self.user_1_folder)

    def test_upload_to_another_users_folder(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(self.url, {'file_field': [self.file1], 'folder_id': self.user_2_folder.id})
        self.assertRedirects(response, reverse('files:drive'))

        uploaded_file = File.objects.get(name="test1.txt")
        self.assertIsNone(uploaded_file.folder)
        self.assertEqual(uploaded_file.owner, self.user1)


class UploadFolderViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = User.objects.create_user(username='user', password='password123')
        self.root_folder = Folder.objects.create(name="Root", owner=self.user)

        self.url = reverse('files:upload_folder')

        self.file1 = SimpleUploadedFile("test1.txt", b"test_content_1")
        self.file2 = SimpleUploadedFile("test2.txt", b"test_content_2")
        self.file3 = SimpleUploadedFile("test3.txt", b"test_content_3")

    def test_get_request_is_rejected(self):
        self.client.login(username='user', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_upload_folder_to_root(self):
        self.client.login(username='user', password='password123')
        response = self.client.post(self.url, {
            'file_field': [self.file1, self.file3],
            'paths': ['Documents/tests/test1.txt', 'Documents/test3.txt']
        })
        self.assertRedirects(response, reverse('files:drive'))

        documents_folder = Folder.objects.filter(name='Documents', owner=self.user, parent=None).first()
        self.assertIsNotNone(documents_folder)

        tests_folder = Folder.objects.filter(name='tests', owner=self.user, parent=documents_folder).first()
        self.assertIsNotNone(tests_folder)

        test_file_1 = File.objects.get(name="test1.txt")
        test_file_3 = File.objects.get(name="test3.txt")

        self.assertEqual(test_file_1.folder, tests_folder)
        self.assertEqual(test_file_3.folder, documents_folder)

    def test_upload_folder_prevents_duplicates(self):
        self.client.login(username='user', password='password123')
        self.client.post(self.url, {
            'file_field': [self.file1, self.file2],
            'paths': ['Documents/test1.txt', 'Documents/test2.txt']
        })

        shared_folders = Folder.objects.filter(name='Documents', owner=self.user)
        self.assertEqual(shared_folders.count(), 1)

        shared_folder = shared_folders.first()
        self.assertEqual(shared_folder.files.count(), 2)

    def test_upload_folder_to_existing_target(self):
        self.client.login(username='user', password='password123')
        response = self.client.post(self.url, {
            'file_field': [self.file1],
            'paths': ['NewDir/test1.txt'],
            'folder_id': self.root_folder.id
        })
        self.assertRedirects(response, reverse('files:drive_folder', kwargs={'folder_id': self.root_folder.id}))

        new_dir_folder = Folder.objects.filter(name='NewDir', owner=self.user).first()
        self.assertEqual(new_dir_folder.parent, self.root_folder)

        file = File.objects.get(name="test1.txt")
        self.assertEqual(file.folder, new_dir_folder)

    def test_upload_with_flat_path_acts_like_standard_upload(self):
        self.client.login(username='user', password='password123')
        self.client.post(self.url, {'file_field': [self.file1], 'paths': ['test1.txt']})

        file = File.objects.get(name="test1.txt")
        self.assertIsNone(file.folder)  # attached straight to root


class DownloadFileViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        file1 = SimpleUploadedFile("test.txt", b"test_content")
        self.valid_file = File.objects.create(file=file1, name="test.txt", size=16, owner=self.user1)
        self.invalid_file = File.objects.create(name="missing.txt", size=0, owner=self.user1)

    def test_unauthenticated_user_redirects_to_login(self):
        url = reverse('files:file_download', kwargs={'pk': self.valid_file.pk})
        response = self.client.get(url)
        self.assertRedirects(response, f'/user/login/?next={url}')

    def test_user_cannot_download_other_users_file(self):
        self.client.login(username='user2', password='password123')
        url = reverse('files:file_download', kwargs={'pk': self.valid_file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_missing_physical_file_raises_404(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:file_download', kwargs={'pk': self.invalid_file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_successful_download_headers_and_response_type(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:file_download', kwargs={'pk': self.valid_file.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response, FileResponse)

        expected_header = f'attachment; filename="{self.valid_file.name}"'
        self.assertEqual(response.headers['Content-Disposition'], expected_header)
        self.assertEqual(b''.join(response.streaming_content), b"test_content")


class DownloadFolderViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.root_folder = Folder.objects.create(name="Documents", owner=self.user1)
        self.sub_folder = Folder.objects.create(name="tests", parent=self.root_folder, owner=self.user1)

        self.file1 = File.objects.create(
            file=SimpleUploadedFile("test1.txt", b"test_content_1"),
            name="test1.txt",
            size=21,
            folder=self.root_folder,
            owner=self.user1
        )
        self.file2 = File.objects.create(
            file=SimpleUploadedFile("test2.txt", b"test_content_2"),
            name="test2.txt",
            size=13,
            folder=self.sub_folder,
            owner=self.user1
        )

        self.url = reverse('files:folder_download', kwargs={'pk': self.root_folder.pk})

    def test_unauthenticated_user_redirects_to_login(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/user/login/?next={self.url}')

    def test_user_cannot_download_other_users_folder(self):
        self.client.login(username='user2', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_successful_zip_download_headers(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertEqual(response['Content-Disposition'], f'attachment; filename="{self.root_folder.name}.zip"')

    def test_zip_archive_integrity_and_hierarchy(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(self.url)
        buffer = io.BytesIO(response.content)

        with zipfile.ZipFile(buffer, 'r') as zip_file:
            zip_contents = zip_file.namelist()

            expected_root_file = "Documents/test1.txt"
            expected_sub_file = "Documents/tests/test2.txt"

            self.assertIn(expected_root_file, zip_contents)
            self.assertIn(expected_sub_file, zip_contents)

            with zip_file.open(expected_root_file) as file:
                self.assertEqual(file.read(), b"test_content_1")


class DeleteFileViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.folder = Folder.objects.create(name="Documents", owner=self.user1)

        self.file1 = File.objects.create(
            file=SimpleUploadedFile("test1.txt", b"test_content_1"),
            name="test1.txt",
            size=12,
            owner=self.user1
        )
        self.file2 = File.objects.create(
            file=SimpleUploadedFile("test2.txt", b"test_content_2"),
            name="test2.txt",
            size=14,
            folder=self.folder,
            owner=self.user1
        )

    def test_get_request_is_rejected(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:file_delete', kwargs={'pk': self.file1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_redirects_to_login(self):
        url = reverse('files:file_delete', kwargs={'pk': self.file1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/user/login/'))
        self.assertEqual(File.objects.filter(pk=self.file1.pk).count(), 1)

    def test_user_cannot_delete_other_users_file(self):
        self.client.login(username='user2', password='password123')
        url = reverse('files:file_delete', kwargs={'pk': self.file1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(File.objects.filter(pk=self.file1.pk).count(), 1)

    def test_successful_deletion_of_root_file(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:file_delete', kwargs={'pk': self.file1.pk})
        physical_file_path = self.file1.file.path
        self.assertTrue(os.path.exists(physical_file_path))

        response = self.client.post(url)
        self.assertRedirects(response, reverse('files:drive'))
        self.assertFalse(File.objects.filter(pk=self.file1.pk).exists())
        self.assertFalse(os.path.exists(physical_file_path))

    def test_successful_deletion_of_nested_file(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:file_delete', kwargs={'pk': self.file2.pk})
        response = self.client.post(url)

        expected_redirect_url = reverse('files:drive_folder', kwargs={'folder_id': self.folder.id})
        self.assertRedirects(response, expected_redirect_url)
        self.assertFalse(File.objects.filter(pk=self.file2.pk).exists())


class DeleteFolderViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')

        self.folder1 = Folder.objects.create(name="Root", owner=self.user1)
        self.file1 = File.objects.create(
            file=SimpleUploadedFile("test1.txt", b"test_content_1"),
            name="test1.txt",
            size=12,
            folder=self.folder1,
            owner=self.user1
        )
        self.folder2 = Folder.objects.create(name="Sub", parent=self.folder1, owner=self.user1)
        self.file2 = File.objects.create(
            file=SimpleUploadedFile("test2.txt", b"test_content_2"),
            name="test2.txt",
            size=11,
            folder=self.folder2,
            owner=self.user1
        )

    def test_get_request_is_rejected(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:folder_delete', kwargs={'pk': self.folder1.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_unauthenticated_user_redirects_to_login(self):
        url = reverse('files:folder_delete', kwargs={'pk': self.folder1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Folder.objects.filter(pk=self.folder1.pk).exists())

    def test_user_cannot_delete_other_users_folder(self):
        self.client.login(username='user2', password='password123')
        url = reverse('files:folder_delete', kwargs={'pk': self.folder1.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Folder.objects.filter(pk=self.folder1.pk).exists())

    def test_successful_deletion_of_nested_folder(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:folder_delete', kwargs={'pk': self.folder2.pk})
        physical_file_path = self.file2.file.path
        self.assertTrue(os.path.exists(physical_file_path))

        response = self.client.post(url)
        expected_redirect_url = reverse('files:drive_folder', kwargs={'folder_id': self.folder1.id})
        self.assertRedirects(response, expected_redirect_url)
        self.assertFalse(Folder.objects.filter(pk=self.folder2.pk).exists())
        self.assertFalse(os.path.exists(physical_file_path))

    def test_successful_deletion_of_root_folder(self):
        self.client.login(username='user1', password='password123')
        url = reverse('files:folder_delete', kwargs={'pk': self.folder1.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse('files:drive'))
        self.assertFalse(Folder.objects.filter(pk=self.folder1.pk).exists())
