from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.projects.models import ResearchProfile, DonationProject
from ddm.participation.models import Participant
from unittest.mock import patch


User = get_user_model()


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

        self.zip_content = b'fake zip content'
        self.zip_file = SimpleUploadedFile(
            "test.zip",
            self.zip_content,
            content_type="application/zip"
        )

    @patch('os.getenv')
    def test_successful_zip_upload(self, mock_getenv):
        mock_getenv.return_value = str(self.blueprint.id)

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
        self.assertEqual(donation.data, self.zip_content)
        self.assertTrue(donation.consent)

    def test_non_zip_file_upload(self):
        txt_file = SimpleUploadedFile(
            "test.txt",
            b"Hello, World!",
            content_type="text/plain"
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
