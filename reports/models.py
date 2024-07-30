import datetime

from ddm.models.encryption import Decryption
from django.conf import settings
from django.db import models
from ddm.models.core import DonationProject, QuestionnaireResponse, DataDonation, DonationBlueprint
from ddm.models.serializers import ResponseSerializer, DonationSerializer


class InstagramStatistics (models.Model):
    name = models.CharField(max_length=30)

    # Vote counts
    biodiversity_counts = models.JSONField(default=None, null=True)
    pension_counts = models.JSONField(default=None, null=True)

    # Party counts
    party_counts = models.JSONField(default=None, null=True)

    # Use counts
    social_media_use = models.JSONField()

    last_updated = models.DateTimeField(null=True, blank=True)
    project_pk = models.IntegerField(default=0)

    def update_vote_counts(self, responses=None):
        if responses is None:
            responses = self.get_responses()

        value_map = {
            '1': 'ja',
            '2': 'nein',
            '3': 'leer',
            '4': 'nicht teilgenommen'
        }
        result_dummy = {
            'ja': 0,
            'nein': 0,
            'leer': 0,
            'nicht teilgenommen': 0
        }

        self.update_bio_count(responses, result_dummy, value_map)
        self.update_pension_count(responses, result_dummy, value_map)
        return

    def update_bio_count(self, responses, result_dummy, value_map):
        if self.biodiversity_counts is None:
            result = result_dummy.copy()
        else:
            result = self.biodiversity_counts.copy()

        var = 'vote-1'
        for response in responses:
            # TODO: Add check that participant has answered question; otherwise skip
            vote = response[var]
            result[value_map[vote]] += 1
        self.biodiversity_counts = result
        return

    def update_pension_count(self, responses, result_dummy, value_map):
        if self.pension_counts is None:
            result = result_dummy.copy()
        else:
            result = self.pension_counts.copy()

        var = 'vote-2'
        for response in responses:
            # TODO: Add check that participant has answered question; otherwise skip
            vote = response[var]
            result[value_map[vote]] += 1
        self.pension_counts = result
        return

    def update_party_graphs(self, responses=None, donations=None, bp_pk=None):
        if responses is None:
            responses = self.get_responses()

        if donations is None:
            donations = self.get_blueprint_donations(bp_pk)

        if self.party_counts is None:
            scale_dummy = {str(i): 0 for i in range(1, 11)}
            self.party_counts = {
                'SP': scale_dummy.copy(),
                'SVP': scale_dummy.copy(),
                'Mitte': scale_dummy.copy(),
                'FDP': scale_dummy.copy()
            }

        for response in responses:
            # get participant id
            participant = None
            # Get var political left/right
            var = 'lrsp'
            # Check if participant has answered the question
            # TODO: Add check that participant has answered question; otherwise skip
            pol_stance = response[var]

            # get donation belonging to response
            response_donation = None
            # compute


        # SP
        # Mitte
        # SVP
        # FDP
        pass

    def update_sm_use(self, responses=None):
        var = 'media_use-4'
        pass

    def get_project(self):
        return DonationProject.objects.get(pk=self.project_pk)

    def get_reference_date(self):
        if self.last_updated is None:
            return datetime.date(2024, 1, 1)
        else:
            return self.last_updated

    def get_decryptor(self, project):
        return Decryption(settings.SECRET_KEY, project.get_salt())

    def get_responses(self):
        project = self.get_project()
        reference_date = self.get_reference_date()

        responses = QuestionnaireResponse.objects.filter(
            project=project, time_submitted__gte=reference_date)

        decryptor = self.get_decryptor(project)
        decrypted_responses = [ResponseSerializer(r, decryptor=decryptor).data['responses'] for r in responses]

        return decrypted_responses

    def get_blueprint_donations(self, bp_pk):
        project = self.get_project()
        reference_date = self.get_reference_date()
        blueprint = DonationBlueprint.objects.get(pk=bp_pk)

        donations = DataDonation.objects.filter(
            blueprint=blueprint, time_submitted__gte=reference_date)

        decryptor = self.get_decryptor(project)
        decrypted_donations = [DonationSerializer(d, decryptor=decryptor).data['data'] for d in donations]

        return decrypted_donations
