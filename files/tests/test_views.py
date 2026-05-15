from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
