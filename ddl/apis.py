import os

from ddm.apis.views import DDMAPIMixin
from ddm.auth.models import ProjectTokenAuthenticator
from ddm.datadonation.models import DataDonation, DonationBlueprint
from ddm.participation.models import Participant
from django.utils import timezone
from dotenv import load_dotenv
from rest_framework import status, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

load_dotenv()


class ZipPostAPI(APIView, DDMAPIMixin):
    """
    Custom view to post zip files to the database and make them accessible
    through the DDM interface and endpoints.
    """
    authentication_classes = [ProjectTokenAuthenticator]
    permission_classes = [permissions.IsAuthenticated]

    def get_project(self):
        project_id = self.kwargs.get('project_url_id')
        return get_object_or_404(DataDonation, url_id=project_id)

    def get_blueprint(self):
        blueprint_id = os.getenv('ZIP_BLUEPRINT_ID')
        return DonationBlueprint.objects.filter(id=blueprint_id).first()

    def post(self, request, *args, **kwargs):
        uploaded_file = request.data['file']
        if not uploaded_file.name.endswith('.zip'):
            return Response(
                {'error': 'Only zip files are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        file_data = uploaded_file.read()
        project = self.get_project()
        blueprint = self.get_blueprint()
        participant = Participant.objects.create(
            project=project,
            start_time=timezone.now(),
            end_time=timezone.now(),
            current_step=3,
        )
        DataDonation.objects.create(
            project=project,
            blueprint=blueprint,
            participant=participant,
            time_submitted=timezone.now(),
            consent=True,
            data=file_data
        )

        return Response(
            'ZIP has been saved in database', status=status.HTTP_201_CREATED)
