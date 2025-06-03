from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.projects.models import ResearchProfile, DonationProject
from ddm.participation.models import Participant
from unittest.mock import patch
import zipfile
import json
from io import BytesIO

User = get_user_model()


class WebsiteUrlTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_robots_txt(self):
        """Test that robots.txt is accessible."""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)

    def test_sitemap(self):
        """Test that sitemap is accessible."""
        response = self.client.get('/sitemap.xml')
        self.assertEqual(response.status_code, 200)


class TestZipPostAPI(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.base_creds = {
            'username': 'owner', 'password': '123', 'email': 'owner@mail.com'
        }
        base_user = User.objects.create_user(**self.base_creds)
        base_profile = ResearchProfile.objects.create(
            user=base_user
        )

        self.project = DonationProject.objects.create(
            name='Test Project',
            slug='zip',
            owner=base_profile
        )
        self.blueprint = DonationBlueprint.objects.create(
            project=self.project,
            name='Test Blueprint',
            description='description',
            exp_file_format='json',
            json_extraction_root='placeholder',
            expected_fields='"field"'
        )

        token = self.project.create_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        json_content = json.dumps({'field': 'value'}).encode('utf-8')
        json_content2 = json.dumps({'field2': 'value2'}).encode('utf-8')
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('test.json', json_content)
            zip_file.writestr('test2.json', json_content2)
        zip_buffer.seek(0)

        self.zip_file = SimpleUploadedFile(
            'test.zip',
            zip_buffer.read(),
            content_type='application/zip'
        )

    @patch('os.getenv')
    def test_successful_zip_upload(self, mock_getenv):
        mock_getenv.return_value = str(self.blueprint.name)

        post_url = reverse(
            'zip_post', kwargs={'project_url_id': self.project.url_id})

        response = self.client.post(
            post_url,
            {'file': self.zip_file},
            format='multipart'
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify database entries
        participant = Participant.objects.last()
        donation = DataDonation.objects.last()
        self.assertIsNotNone(donation)
        self.assertEqual(donation.project, self.project)
        self.assertEqual(donation.blueprint, self.blueprint)
        self.assertEqual(donation.participant, participant)
        self.assertTrue(donation.consent)

        # Verify saved data
        expected_data = {
            'test.json': {'field': 'value'},
            'test2.json': {'field2': 'value2'}
        }
        saved_data = donation.get_decrypted_data(
            self.project.secret, self.project.get_salt())
        self.assertEqual(saved_data, expected_data)

    def test_non_zip_file_upload(self):
        txt_file = SimpleUploadedFile(
            'test.txt',
            b'Hello, World!',
            content_type='text/plain'
        )
        post_url = reverse(
            'zip_post', kwargs={'project_url_id': self.project.url_id})
        response = self.client.post(
            post_url,
            {'file': txt_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {'error': 'Only zip files are allowed.'})

    def test_corrupted_zip_upload(self):
        corrupted_zip_file = SimpleUploadedFile(
            'corrupt.zip',
            b'not a real zip file',
            content_type='application/zip'
        )
        post_url = reverse(
            'zip_post', kwargs={'project_url_id': self.project.url_id})
        response = self.client.post(
            post_url,
            {'file': corrupted_zip_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_json_in_zip(self):
        invalid_json_zip_buffer = BytesIO()
        with zipfile.ZipFile(invalid_json_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('invalid.json', '{invalid json')
        invalid_json_zip_buffer.seek(0)

        invalid_zip_file = SimpleUploadedFile(
            'invalid.zip',
            invalid_json_zip_buffer.read(),
            content_type='application/zip'
        )

        post_url = reverse(
            'zip_post', kwargs={'project_url_id': self.project.url_id})
        response = self.client.post(
            post_url,
            {'file': invalid_zip_file},
            format='multipart'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid JSON format', response.data['errors']['invalid.json']['error'])

    @patch('os.getenv')
    def test_partial_invalid_json_in_zip(self, mock_getenv):
        mock_getenv.return_value = str(self.blueprint.name)

        json_zip_buffer = BytesIO()
        with zipfile.ZipFile(json_zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('invalid.json', '{invalid json')
            zip_file.writestr('valid.json', '{"field": "value"}')
        json_zip_buffer.seek(0)

        invalid_zip_file = SimpleUploadedFile(
            'file.zip',
            json_zip_buffer.read(),
            content_type='application/zip'
        )

        post_url = reverse(
            'zip_post', kwargs={'project_url_id': self.project.url_id})
        response = self.client.post(
            post_url,
            {'file': invalid_zip_file},
            format='multipart'
        )

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify database entries
        participant = Participant.objects.last()
        donation = DataDonation.objects.last()
        self.assertIsNotNone(donation)
        self.assertEqual(donation.project, self.project)
        self.assertEqual(donation.blueprint, self.blueprint)
        self.assertEqual(donation.participant, participant)
        self.assertTrue(donation.consent)

        # Verify saved data
        expected_data = {
            'invalid.json': {'error': 'Invalid JSON format'},
            'valid.json': {'field': 'value'}
        }
        saved_data = donation.get_decrypted_data(
            self.project.secret, self.project.get_salt())
        self.assertEqual(saved_data, expected_data)
