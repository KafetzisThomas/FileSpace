from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
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
