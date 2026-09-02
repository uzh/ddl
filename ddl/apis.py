import json
import os
import zipfile
from io import BytesIO

from ddm.apis.views import DDMAPIMixin
from ddm.auth.models import ProjectTokenAuthenticator
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.participation.models import Participant
from ddm.projects.models import DonationProject
from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from dotenv import load_dotenv
from rest_framework import permissions, status
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

    Endpoint: `/api/zip/<project_url_id>`
    Method: `POST`

    Authentication:
    - Requires `Token Authentication` using a `ProjectAccessToken`.
    - Only authenticated users can access this endpoint.

    Request Format:
    - Content-Type: `multipart/form-data`
    - Required fields:
      - `file`: A ZIP file containing one or more JSON files.

    The target `DonationBlueprint` is resolved by name from the
    `ZIP_BLUEPRINT_NAME` environment variable.

    Response Codes:
    - `201 Created`: When the ZIP is successfully processed and stored.
    - `400 Bad Request`: If an invalid ZIP is uploaded or JSON is malformed.
    - `404 Not Found`: If the project or blueprint is not found.

    Example Request:
    curl -X POST https://<main_domain>/api/zip/<project_url_id> \
    -H "Authorization: Token <your_project_token>" \
    -F file=@your_zip_file.zip
    """

    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def setup(self, request: HttpRequest, *args, **kwargs) -> None:
        super().setup(request, *args, **kwargs)
        self.project = self.get_project()
        self.blueprint = self.get_blueprint()

    def get_project(self) -> DonationProject:
        project_id = self.kwargs.get("project_url_id")
        return get_object_or_404(DonationProject, url_id=project_id)

    def get_blueprint(self) -> DonationBlueprint | None:
        blueprint_name = self.kwargs.get("blueprint_name", None)
        if blueprint_name is None:
            blueprint_name = os.getenv("ZIP_BLUEPRINT_NAME")
        return DonationBlueprint.objects.filter(
            name=blueprint_name, project=self.project
        ).first()

    def create_participant(self) -> Participant:
        return Participant.objects.create(
            project=self.project,
            start_time=timezone.now(),
            end_time=timezone.now(),
            current_step=3,
        )

    def create_donation(self, participant: Participant, data: dict) -> DataDonation:
        return DataDonation.objects.create(
            project=self.project,
            blueprint=self.blueprint,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data=data,
            status="success",
        )

    @staticmethod
    def _check_zip_safety(zip_ref: zipfile.ZipFile) -> None:
        """Reject oversized archives and zip bombs before reading any member."""
        infos = zip_ref.infolist()
        if len(infos) > settings.ZIP_UPLOAD_MAX_MEMBERS:
            raise ValidationError({"error": "ZIP contains too many files."})

        total_uncompressed = 0
        for info in infos:
            total_uncompressed += info.file_size
            if total_uncompressed > settings.ZIP_UPLOAD_MAX_UNCOMPRESSED_BYTES:
                raise ValidationError(
                    {"error": "Uncompressed ZIP content exceeds the allowed size."}
                )
            ratio = info.file_size / info.compress_size if info.compress_size else 0
            if ratio > settings.ZIP_UPLOAD_MAX_COMPRESSION_RATIO:
                raise ValidationError(
                    {"error": "ZIP rejected: suspicious compression ratio."}
                )

    @staticmethod
    def _load_json_member(json_file: zipfile.ZipExtFile) -> object:
        """Read a single member with a hard byte cap (declared sizes can lie)."""
        max_bytes = settings.ZIP_UPLOAD_MAX_UNCOMPRESSED_BYTES
        raw = json_file.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise ValidationError(
                {"error": "Uncompressed ZIP content exceeds the allowed size."}
            )
        return json.loads(raw)

    @classmethod
    def extract_zip(cls, file_data: bytes) -> tuple[dict, dict]:
        result = {}
        errors = {}

        try:
            with zipfile.ZipFile(BytesIO(file_data), "r") as zip_ref:
                cls._check_zip_safety(zip_ref)
                for file_name in zip_ref.namelist():
                    if file_name.endswith(".json"):
                        with zip_ref.open(file_name) as json_file:
                            try:
                                file_content = cls._load_json_member(json_file)
                                result[file_name] = file_content
                            except json.JSONDecodeError:
                                msg = {"error": "Invalid JSON format"}
                                errors[file_name] = msg
                                result[file_name] = msg
        except zipfile.BadZipFile as e:
            raise ValidationError({"error": "Invalid or corrupted ZIP file."}) from e

        return result, errors

    def post(self, request: HttpRequest, *args, **kwargs) -> Response:
        # Extract files.
        uploaded_file = request.data.get("file")
        if uploaded_file is None:
            return Response(
                {"error": "No file was submitted."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not uploaded_file.name.endswith(".zip"):
            return Response(
                {"error": "Only zip files are allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded_file.size > settings.ZIP_UPLOAD_MAX_BYTES:
            return Response(
                {"error": "Uploaded ZIP file is too large."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_data = uploaded_file.read()
        result, errors = self.extract_zip(file_data)

        if errors and not len(result.keys()) > len(errors.keys()):
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        participant = self.create_participant()
        self.create_donation(participant, result)

        return Response(
            "ZIP has been saved in database", status=status.HTTP_201_CREATED
        )
