import copy
import json
import os

import requests
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Legend, Span
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

from django.conf import settings
from django.views.generic import TemplateView

from .models import InstagramStatistics
from . import graphs

from requests import JSONDecodeError


class BaseReport:
    project_pk = None
    donation_endpoint = 'https://datadonation.uzh.ch/ddm/api/project/<project_p>/donations'
    response_endpoint = 'https://datadonation.uzh.ch/ddm/api/project/<project_p>/responses'
    token = None

    def get_donation_endpoint(self):
        """ Overwrite this method to return the API endpoint. """
        return self.donation_endpoint.replace('<project_p>', f'{self.project_pk}')

    def get_response_endpoint(self):
        """ Overwrite this method to return the API endpoint. """
        return self.response_endpoint.replace('<project_p>', f'{self.project_pk}')

    def get_token(self):
        """ Overwrite this method to return the API token. """
        return self.token

    def get_headers(self):
        return {'Authorization': f'Token {self.get_token()}'}

    def get_payload(self):
        return {'participants': self.kwargs.get('participant_id')}

    def get_data(self, payload=None):
        """ Retrieve data from DDM. """
        payload = self.get_payload() if payload is None else payload
        r = requests.get(self.get_donation_endpoint(), headers=self.get_headers(), params=payload)

        if r.ok:
            try:
                return r.json()
            except JSONDecodeError:
                return '{"errors": ["JSONDecodeError"]}'
        else:
            return '{}'

    def get_responses(self, payload=None):
        """ Retrieve data from DDM. """
        payload = self.get_payload() if payload is None else payload
        r = requests.get(self.get_response_endpoint(), headers=self.get_headers(), params=payload)

        if r.ok:
            try:
                return r.json()
            except JSONDecodeError:
                return '{"errors": ["JSONDecodeError"]}'
        else:
            return '{}'


class PoliticsReportInstagram(BaseReport, TemplateView):
    template_name = 'reports/politics_instagram.html'
    project_pk = 21
    donation_endpoint = 'https://datadonation.uzh.ch/ddm/api/project/21/donations?participants=<participant_id>'
    token = settings.POLITICS_KEY_INSTAGRAM

    @staticmethod
    def load_insta_account_list():
        path_insta_accounts = os.path.join(settings.BASE_DIR, 'reports/static/reports/data/insta_accounts_complete.json')
        with open(path_insta_accounts) as f:
            insta_accounts = json.load(f)
            insta_accounts = json.loads(json.dumps(insta_accounts).encode('latin1').decode('utf-8'))
        return insta_accounts

    def get_follows_insta(self, data, insta_accounts):
        bp_name = 'Gefolgte KanÃ¤le Instagram'  # 'Gefolgte Kanäle Instagram'
        if bp_name not in data:
            return None, None
        if data[bp_name] is None:
            return None, None

        n_follows_insta = len(data[bp_name][0])

        followed_accounts = {
            'parties': [],
            'media': [],
            'politicians': [],
            'organisations': [],
            'other': []
        }

        for account in data[bp_name][0]:
            profile = account['string_list_data'][0]['href']

            if profile in insta_accounts.keys():
                insta_profile = insta_accounts[profile]

                if insta_profile['type'] == 'media':
                    followed_accounts['media'].append(profile)
                elif insta_profile['type'] == 'organisation':
                    followed_accounts['organisations'].append(profile)
                elif insta_profile['type'] == 'party':
                    followed_accounts['parties'].append(profile)
                elif insta_profile['type'] == 'politician':
                    followed_accounts['politicians'].append(profile)
            else:
                followed_accounts['other'].append(profile)

        return followed_accounts, n_follows_insta

    def get_interactions_insta(self, data, insta_accounts):
        # TODO: Delete if not used
        # insta_names = {}
        # for profile, vars in insta_accounts.items:
        #     insta_names[vars['name']] = {'url': profile}
        #     for var in vars.keys():
        #         if var != 'name':
        #             insta_names[vars['name']][var] = vars[var]

        bp_names = [
            'Gelikte Posts Instagram',
            'Story Likes Instagram',
            'Kommentare Instagram',
            'Reels Kommentare Instagram'
        ]
        interaction_keys = [
            'likes_posts',
            'likes_stories',
            'comments_general',
            'comments_reels'
        ]
        value_placeholder = {
            'media': [],
            'organisations': [],
            'parties': [],
            'politicians': [],
            'other': []
        }
        interactions = {key: copy.deepcopy(value_placeholder) for key in interaction_keys}

        for index, bp_name in enumerate(bp_names):
            if bp_name not in data:
                continue
            if data[bp_name] is None:
                continue

            key = interaction_keys[index]

            for account in data[bp_name][0]:
                profile = 'https://www.instagram.com/' + account['title'].strip()

                if profile in insta_accounts.keys():
                    insta_profile = insta_accounts[profile]

                    if insta_profile['type'] == 'media':
                        interactions[key]['media'].append(profile)
                    elif insta_profile['type'] == 'organisation':
                        interactions[key]['organisations'].append(profile)
                    elif insta_profile['type'] == 'party':
                        interactions[key]['parties'].append(profile)
                    elif insta_profile['type'] == 'politician':
                        interactions[key]['politicians'].append(profile)
                else:
                    interactions[key]['other'].append(profile)

        return interactions

    def get_proposed_content_insta(self, data, insta_accounts):
        bp_names = [
            'Geschaute Werbung Instagram',
            'Vorgeschlagene Profile',
            'Geschaute Posts Instagram',
            'Geschaute Videos Instagram'
        ]
        content_keys = [
            'seen_ads',
            'recommended_profiles',
            'seen_posts',
            'seen_videos'
        ]
        value_placeholder = {
            'media': [],
            'organisations': [],
            'parties': [],
            'politicians': [],
            'other': []
        }
        content = {key: copy.deepcopy(value_placeholder) for key in content_keys}

        for index, bp_name in enumerate(bp_names):

            if bp_name not in data:
                continue
            if data[bp_name] in [None, []]:
                continue

            key = content_keys[index]
            for account in data[bp_name][0]:
                try:
                    profile = 'https://www.instagram.com/' + account['string_map_data']['Author']['value'].strip()
                except:
                    continue

                if profile in insta_accounts.keys():
                    insta_profile = insta_accounts[profile]

                    if insta_profile['type'] == 'media':
                        content[key]['media'].append(profile)
                    elif insta_profile['type'] == 'organisation':
                        content[key]['organisations'].append(profile)
                    elif insta_profile['type'] == 'party':
                        content[key]['parties'].append(profile)
                    elif insta_profile['type'] == 'politician':
                        content[key]['politicians'].append(profile)
                else:
                    content[key]['other'].append(profile)
        return content

    def add_response_context(self, context):
        # TODO: Enable in production
        # responses_api = self.get_responses()
        # context['responses_api'] = responses_api[0]

        # TODO: Disable in production
        file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/politics_responses.json')
        with open(file_path, encoding='latin1') as f:
            responses = json.load(f)

        context['responses_file'] = responses

        stats = InstagramStatistics()
        stats.project_pk = 4
        stats.update_vote_counts()
        context['responses'] = stats.get_responses()
        context['counts_bio'] = stats.biodiversity_counts
        context['counts_pension'] = stats.pension_counts

        # TODO
        # Graph biodiversity (overall count - yes vs. no)
        context['biodiversity_graph'] = graphs.get_vote_graph(stats.biodiversity_counts)

        # Graph pension reform (overall count - yes vs. no)
        context['pension_graph'] = graphs.get_vote_graph(stats.pension_counts, color='2')

        # Graph partie following (count follows per point on left-right scale)
        context['donations'] = stats.get_blueprint_donations(12)

        ## Party Graphs
        context['sp_graph'] = graphs.get_party_graph(None, 'SP')
        context['svp_graph'] = graphs.get_party_graph(None, 'SVP')
        context['mitte_graph'] = graphs.get_party_graph(None, 'Mitte')
        context['fdp_graph'] = graphs.get_party_graph(None, 'FDP')

        # Social Media for information (left vs. right

        return

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # data = self.get_data()  TODO: Enable when in production

        file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/politics_data.json')
        with open(file_path, encoding='latin1') as f:
            data = json.load(f)
        context['test_data'] = json.dumps(data).encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')

        # Variables
        donation_instagram = None  # Boolean TODO
        donation_facebook = None  # Boolean TODO

        insta_account_list = self.load_insta_account_list()
        followed_accounts, n_insta_accounts = self.get_follows_insta(data, insta_account_list)
        insta_interactions = self.get_interactions_insta(data, insta_account_list)
        insta_proposed_content = self.get_proposed_content_insta(data, insta_account_list)

        context['n_follows'] = n_insta_accounts
        context['n_follows_relevant'] = n_insta_accounts - len(followed_accounts['other'])

        # Graph 1: n per account category
        context['insta_follows_plot'] = graphs.get_insta_follows_plot(followed_accounts)

        # Graph 2: account category axis + comparison
        context['insta_line_plot'] = graphs.get_insta_line_plot(followed_accounts, n_insta_accounts)

        # Graph 3: interaction bar plot per category
        context['insta_interaction_plot'] = graphs.get_interaction_plot(insta_interactions)

        # Graph 4: proposed content bar plot per category
        context['insta_content_plot'] = graphs.get_content_plot(insta_proposed_content)

        self.add_response_context(context)

        return context


class PoliticsReportFacebook(BaseReport, TemplateView):
    template_name = 'reports/politics_facebook.html'
    project_pk = 27
    token = settings.POLITICS_KEY_FACEBOOK


class SearchReport(BaseReport, TemplateView):
    template_name = 'reports/search_report.html'
    project_pk = 26
    token = settings.SEARCH_KEY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_donation_context(context)
        return context

    def get_donation_context(self, context):
        # TODO: Enable when in production
        # data = self.get_data()

        # TODO: Disable in production:
        file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/search_data.json')
        with open(file_path, encoding='latin1') as f:
            data = json.load(f)
        context['test_data'] = data
        return


class DigitalMealReport(BaseReport, TemplateView):
    template_name = 'reports/digital_meal.html'
    project_pk = None
    token = settings.DIGITAL_MEAL_KEY


class ChatGPTReport(BaseReport, TemplateView):
    template_name = 'reports/chatgpt.html'
    project_pk = None
    token = settings.CHATGPT_KEY


# TODO: Delete
"""
For console to load xlsx files:
import json
import os

cur_dir = os.path.dirname(os.path.realpath(__file__))
file_path = './ddl/reports/static/temp/media.xlsx'

f = pd.read_excel(os.path.join(cur_dir, path))
f_json = json.loads(f.to_json(orient='records')
"""
