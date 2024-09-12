import datetime

from ddm.models.encryption import Decryption
from django.conf import settings
from django.db import models
from ddm.models.core import DonationProject, QuestionnaireResponse, DataDonation, DonationBlueprint
from ddm.models.serializers import ResponseSerializer, DonationSerializer

from .utils import insta_data


class InstagramStatistics (models.Model):
    name = models.CharField(max_length=30)

    # Follow counts
    follow_counts = models.JSONField(default=None, null=True)

    # Vote counts
    biodiversity_counts = models.JSONField(default=None, null=True)
    pension_counts = models.JSONField(default=None, null=True)

    # Party counts
    party_counts = models.JSONField(default=None, null=True)

    # Use counts
    social_media_use = models.JSONField(default=None, null=True)

    last_updated = models.DateTimeField(null=True, blank=True)
    project_pk = models.IntegerField(default=0)

    def update_statistics(self):
        new_responses = self.get_responses()
        new_donations = self.get_blueprint_donations(settings.BP_ID_FOLLOWED_ACCOUNTS)

        self.update_followed_accounts(new_donations)
        self.update_vote_counts(new_responses)  # bio & pension
        self.update_party_graphs(new_responses, new_donations)
        self.last_updated = datetime.datetime.now()
        self.save()

    def update_followed_accounts(self, donations=None, bp_pk=None):
        if donations is None:
            donations = self.get_blueprint_donations(settings.BP_ID_FOLLOWED_ACCOUNTS)

        insta_accounts = insta_data.load_political_account_list()
        results = []
        for p, d in donations.items():
            data = {'Gefolgte Kanäle Instagram': [d]}
            followed_accounts = insta_data.get_follows_insta(data, insta_accounts)
            if followed_accounts:
                results.append(followed_accounts.copy())

        if self.follow_counts is None:
            self.follow_counts = insta_data.TYPES_DICT_PLACEHOLDER.copy()

        for r in results:
            for k in r.keys():
                self.follow_counts[k].append(len(r[k]))
        return

    def get_follow_counts(self):
        for c, counts in self.follow_counts.items():
            if not counts:
                return None
        return self.follow_counts

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
        for p, r in responses.items():
            if var in r.keys():
                vote = r[var]
            else:
                continue
            if vote in value_map.keys():
                result[value_map[vote]] += 1
        self.biodiversity_counts = result
        return

    def update_pension_count(self, responses, result_dummy, value_map):
        if self.pension_counts is None:
            result = result_dummy.copy()
        else:
            result = self.pension_counts.copy()

        var = 'vote-2'
        for p, r in responses.items():
            if var in r.keys():
                vote = r[var]
            else:
                continue
            if vote in value_map.keys():
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

        for participant, response in responses.items():
            if not (participant in responses.keys() and participant in donations.keys()):
                continue

            var = 'lrsp'
            if var in response.keys():
                pol_stance = response[var]
            else:
                continue

            valid_responses = [str(i) for i in range(1, 11)]
            if pol_stance not in valid_responses:
                continue

            donation = donations[participant]
            political_accounts = insta_data.load_political_account_list()
            parties = ['SP', 'SVP', 'Mitte', 'FDP']
            p_follows_party = {p: False for p in parties}
            for account in donation:
                profile = account['string_list_data'][0]['href']
                if profile in political_accounts.keys():
                    insta_profile = political_accounts[profile]
                    profile_type = insta_profile['type']
                    if profile_type != 'party':
                        continue
                    profile_party = insta_profile['party']
                    if profile_party in parties:
                        p_follows_party[profile_party] = True

            # Add to result
            for party, follows in p_follows_party.items():
                if follows:
                    self.party_counts[party][pol_stance] += 1
        return

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
        """
        Returns dictionary with responses per participant.
        {'participant_id': {'response-var': <response>, ...}}
        """
        project = self.get_project()
        reference_date = self.get_reference_date()

        responses = QuestionnaireResponse.objects.filter(
            project=project, time_submitted__gte=reference_date)

        decryptor = self.get_decryptor(project)
        decrypted_responses = {}
        for r in responses:
            serialized_r = ResponseSerializer(r, decryptor=decryptor)
            decrypted_responses[serialized_r.data['participant']] = serialized_r.data['responses']
        return decrypted_responses

    def get_blueprint_donations(self, bp_pk):
        """
        Returns dictionary with donations per participant.
        {'participant_id': <extracted donation>}
        """
        project = self.get_project()
        reference_date = self.get_reference_date()
        blueprint = DonationBlueprint.objects.get(pk=bp_pk)

        donations = DataDonation.objects.filter(
            blueprint=blueprint, time_submitted__gte=reference_date)

        decryptor = self.get_decryptor(project)
        decrypted_donations = {}
        for d in donations:
            serialized_d = DonationSerializer(d, decryptor=decryptor)
            decrypted_donations[serialized_d.data['participant']] = serialized_d.data['data']
        return decrypted_donations


class FacebookStatistics(InstagramStatistics):

    def update_statistics(self):
        new_responses = self.get_responses()
        new_donations = self.get_blueprint_donations(settings.BP_ID_FOLLOWED_ACCOUNTS)    # TODO: Adjust

        self.update_followed_accounts(new_donations)
        self.update_vote_counts(new_responses)  # bio & pension
        self.update_party_graphs(new_responses, new_donations)
        self.last_updated = datetime.datetime.now()
        self.save()

    def update_followed_accounts(self, donations=None, bp_pk=None):  # TODO: Adjust
        if donations is None:
            donations = self.get_blueprint_donations(settings.BP_ID_FOLLOWED_ACCOUNTS)

        insta_accounts = insta_data.load_political_account_list()
        results = []
        for p, d in donations.items():
            data = {'Gefolgte Seiten Facebook': [d]}
            followed_accounts = insta_data.get_follows_insta(data, insta_accounts)
            if followed_accounts:
                results.append(followed_accounts.copy())

        if self.follow_counts is None:
            self.follow_counts = insta_data.TYPES_DICT_PLACEHOLDER.copy()

        for r in results:
            for k in r.keys():
                self.follow_counts[k].append(len(r[k]))
        return

    # def get_follow_counts(self):
    #     for c, counts in self.follow_counts.items():
    #         if not counts:
    #             return None
    #     return self.follow_counts

    # def update_vote_counts(self, responses=None):
    #     if responses is None:
    #         responses = self.get_responses()
    #
    #     value_map = {
    #         '1': 'ja',
    #         '2': 'nein',
    #         '3': 'leer',
    #         '4': 'nicht teilgenommen'
    #     }
    #     result_dummy = {
    #         'ja': 0,
    #         'nein': 0,
    #         'leer': 0,
    #         'nicht teilgenommen': 0
    #     }
    #
    #     self.update_bio_count(responses, result_dummy, value_map)
    #     self.update_pension_count(responses, result_dummy, value_map)
    #     return

    # def update_bio_count(self, responses, result_dummy, value_map):
    #     if self.biodiversity_counts is None:
    #         result = result_dummy.copy()
    #     else:
    #         result = self.biodiversity_counts.copy()
    #
    #     var = 'vote-1'
    #     for p, r in responses.items():
    #         if var in r.keys():
    #             vote = r[var]
    #         else:
    #             continue
    #         if vote in value_map.keys():
    #             result[value_map[vote]] += 1
    #     self.biodiversity_counts = result
    #     return

    # def update_pension_count(self, responses, result_dummy, value_map):
    #     if self.pension_counts is None:
    #         result = result_dummy.copy()
    #     else:
    #         result = self.pension_counts.copy()
    #
    #     var = 'vote-2'
    #     for p, r in responses.items():
    #         if var in r.keys():
    #             vote = r[var]
    #         else:
    #             continue
    #         if vote in value_map.keys():
    #             result[value_map[vote]] += 1
    #     self.pension_counts = result
    #     return

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

        for participant, response in responses.items():
            if not (participant in responses.keys() and participant in donations.keys()):
                continue

            var = 'lrsp'
            if var in response.keys():
                pol_stance = response[var]
            else:
                continue

            valid_responses = [str(i) for i in range(1, 11)]
            if pol_stance not in valid_responses:
                continue

            donation = donations[participant]
            political_accounts = insta_data.load_political_account_list()
            parties = ['SP', 'SVP', 'Mitte', 'FDP']
            p_follows_party = {p: False for p in parties}
            for account in donation:
                profile = account['title']  # TODO: Account for both
                if profile in political_accounts.keys():
                    insta_profile = political_accounts[profile]
                    profile_type = insta_profile['type']
                    if profile_type != 'party':
                        continue
                    profile_party = insta_profile['party']
                    if profile_party in parties:
                        p_follows_party[profile_party] = True

            # Add to result
            for party, follows in p_follows_party.items():
                if follows:
                    self.party_counts[party][pol_stance] += 1
        return

    # def get_project(self):
    #     return DonationProject.objects.get(pk=self.project_pk)

    # def get_reference_date(self):
    #     if self.last_updated is None:
    #         return datetime.date(2024, 1, 1)
    #     else:
    #         return self.last_updated

    # def get_decryptor(self, project):
    #     return Decryption(settings.SECRET_KEY, project.get_salt())

    # def get_responses(self):
    #     """
    #     Returns dictionary with responses per participant.
    #     {'participant_id': {'response-var': <response>, ...}}
    #     """
    #     project = self.get_project()
    #     reference_date = self.get_reference_date()
    #
    #     responses = QuestionnaireResponse.objects.filter(
    #         project=project, time_submitted__gte=reference_date)
    #
    #     decryptor = self.get_decryptor(project)
    #     decrypted_responses = {}
    #     for r in responses:
    #         serialized_r = ResponseSerializer(r, decryptor=decryptor)
    #         decrypted_responses[serialized_r.data['participant']] = serialized_r.data['responses']
    #     return decrypted_responses

    # def get_blueprint_donations(self, bp_pk):
    #     """
    #     Returns dictionary with donations per participant.
    #     {'participant_id': <extracted donation>}
    #     """
    #     project = self.get_project()
    #     reference_date = self.get_reference_date()
    #     blueprint = DonationBlueprint.objects.get(pk=bp_pk)
    #
    #     donations = DataDonation.objects.filter(
    #         blueprint=blueprint, time_submitted__gte=reference_date)
    #
    #     decryptor = self.get_decryptor(project)
    #     decrypted_donations = {}
    #     for d in donations:
    #         serialized_d = DonationSerializer(d, decryptor=decryptor)
    #         decrypted_donations[serialized_d.data['participant']] = serialized_d.data['data']
    #     return decrypted_donations
