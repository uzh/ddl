import json
import os
import zipfile
from io import BytesIO

from ddm.apis.views import DDMAPIMixin
from ddm.auth.models import ProjectTokenAuthenticator
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from django.utils import timezone
from dotenv import load_dotenv
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

load_dotenv()


class ZipPostAPI(APIView, DDMAPIMixin):
    """
    This endpoint allows users to upload a ZIP file containing one or several
    JSON files. The extracted JSON data is encrypted and stored in the
    database in a `DataDonation` linked to a `Participant` and
    `DonationBlueprint`.

    Endpoint: `/api/zip-post/<project_url_id>/`
    Method: `POST`

    Authentication:
    - Requires `Token Authentication` using a ` ProjectAccessToken`.
    - Only authenticated users can access this endpoint.

    Request Format:
    - Content-Type: `multipart/form-data`
    - Required fields:
      - `file`: A ZIP file containing one or more JSON files.
    - Optional URL request parameters:
      - blueprint_name: Only required if you want to overwrite the
        default blueprint_name (“D2USP_Default”).

    Response Codes:
    - `201 Created` – When the ZIP is successfully processed and stored.
    - `400 Bad Request` – If an invalid ZIP is uploaded or JSON is malformed.
    - `404 Not Found` – If the project or blueprint is not found.

    Example Request:
    curl -X POST https://<main_domain>/api/zip-post/<project_url_id>/ \
    -H "Authorization: Token <your_project_token>" \
    -F file=@your_zip_file.zip
    """
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.project = self.get_project()
        self.blueprint = self.get_blueprint()

    def get_project(self):
        project_id = self.kwargs.get('project_url_id')
        return get_object_or_404(DonationProject, url_id=project_id)

    def get_blueprint(self):
        blueprint_name = self.kwargs.get('blueprint_name', None)
        if blueprint_name is None:
            blueprint_name = os.getenv('ZIP_BLUEPRINT_NAME')
        return DonationBlueprint.objects.filter(
            name=blueprint_name, project=self.project
        ).first()

    def create_participant(self):
        return Participant.objects.create(
            project=self.project,
            start_time=timezone.now(),
            end_time=timezone.now(),
            current_step=3,
        )

    def create_donation(self, participant, data):
        return DataDonation.objects.create(
            project=self.project,
            blueprint=self.blueprint,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data=data,
            status='success'
        )

    @staticmethod
    def extract_zip(file_data):
        result = {}
        errors = {}

        try:
            with zipfile.ZipFile(BytesIO(file_data), 'r') as zip_ref:
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.json'):
                        with zip_ref.open(file_name) as json_file:
                            try:
                                file_content = json.load(json_file)
                                result[file_name] = file_content
                            except json.JSONDecodeError:
                                msg = {'error': 'Invalid JSON format'}
                                errors[file_name] = msg
                                result[file_name] = msg
        except zipfile.BadZipFile:
            raise ValidationError({'error': 'Invalid or corrupted ZIP file.'})

        return result, errors

    def post(self, request, *args, **kwargs):
        # Extract files.
        uploaded_file = request.data['file']
        if not uploaded_file.name.endswith('.zip'):
            return Response(
                {'error': 'Only zip files are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_data = uploaded_file.read()
        result, errors = self.extract_zip(file_data)

        if errors and not len(result.keys()) > len(errors.keys()):
            return Response(
                {'errors': errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        participant = self.create_participant()
        self.create_donation(participant, result)

        return Response(
            'ZIP has been saved in database',
            status=status.HTTP_201_CREATED
        )
