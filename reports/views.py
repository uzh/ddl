import copy
import json
import os

import requests
from bokeh.embed import components
from bokeh.models import ColumnDataSource, FactorRange, Legend
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

from django.conf import settings
from django.views.generic import TemplateView

from requests import JSONDecodeError


class BaseReport:
    project_pk = None
    donation_endpoint = 'https://datadonation.uzh.ch/ddm/api/project/<project_p>/donations'
    token = None

    def get_donation_endpoint(self):
        """ Overwrite this method to return the API endpoint. """
        return self.donation_endpoint.replace('<project_p>', f'{self.project_pk}')

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


class PoliticsReport(BaseReport, TemplateView):
    template_name = 'reports/politics_report.html'
    project_pk = 21
    donation_endpoint = 'https://datadonation.uzh.ch/ddm/api/project/21/donations?participants=<participant_id>'
    token = settings.POLITICS_KEY

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

        n_follows_insta = len(data[bp_name])

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

    def get_custom_legend(self, p):
        label_colors = {
            'Parteien': '#de0c1c',
            'Politiker:innen': '#fe2d2d',
            'Medien': '#fb7830',
            'Organisationen': '#fecf02',
            'andere': '#ffeea3'
        }
        categories = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen', 'andere']
        legend_items = [(label, [p.square(-10, -10, legend_label=label, color=label_colors[label])]) for label in categories]
        legend = Legend(items=legend_items, location='center',
                        background_fill_color=None, border_line_color=None,
                        orientation='horizontal')
        return legend

    def get_insta_follows_plot(self, followed_accounts):
        n_total = sum([len(followed_accounts[key]) for key in followed_accounts.keys()])
        fractions = {key: (len(followed_accounts[key]) / n_total) for key in followed_accounts.keys()}

        print(fractions)

        dimension = ['Gefolgte Accounts']
        categories = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen', 'andere']
        palette = ['#de0c1c', '#fe2d2d', '#fb7830', '#fecf02', '#ffeea3']

        data = {
            'Gefolgte Accounts': dimension,
            'Parteien': [len(followed_accounts['parties'])],
            'Politiker:innen': [len(followed_accounts['politicians'])],
            'Medien': [len(followed_accounts['media'])],
            'Organisationen': [len(followed_accounts['organisations'])],
            'andere': [len(followed_accounts['other'])],
        }
        print(data)
        p = figure(y_range=dimension, x_range=(0, n_total), height=200, width=800, toolbar_location=None,
                   tools='hover', tooltips='$name: @$name',
                   background_fill_color=None)

        p.hbar_stack(categories, y='Gefolgte Accounts', height=0.9, color=palette, source=ColumnDataSource(data),
                     legend_label=categories)

        p.border_fill_color = None
        p.y_range.range_padding = 0.1
        p.yaxis.visible = False
        p.ygrid.visible = False
        p.xgrid.visible = False
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None

        p.legend.visible = False
        legend = self.get_custom_legend(p)
        p.add_layout(legend, 'below')

        script, div = components(p)
        return {'script': script, 'div': div}

    def get_interaction_plot(self, interactions):
        def get_list_for_plot(category, interactions):
            l = []
            for interaction in ['likes_posts', 'likes_stories', 'comments_general', 'comments_reels']:
                l.append(len(interactions[interaction][category]))
            return l

        interaction_types = [
            'Likes Posts',              # 'likes_posts',
            'Likes Stories',            # 'likes_stories',
            'Kommentare allgemein',     # 'comments_general',
            'Kommentare Reels'          # 'comments_reels'
        ]
        categories = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen', 'andere']
        data = {
            'interactions': interaction_types,
            'Parteien': get_list_for_plot('parties', interactions),
            'Politiker:innen': get_list_for_plot('politicians', interactions),
            'Medien': get_list_for_plot('media', interactions),
            'Organisationen': get_list_for_plot('organisations', interactions),
            'andere': get_list_for_plot('other', interactions),
        }

        palette = ['#de0c1c', '#fe2d2d', '#fb7830', '#fecf02', '#ffeea3']
        x = [(interaction, category) for interaction in interaction_types for category in categories]
        counts = sum(zip(data['Parteien'], data['Politiker:innen'], data['Medien'], data['Organisationen'], data['andere']), ())  # like an hstack
        source = ColumnDataSource(data=dict(x=x, counts=counts))

        p = figure(x_range=FactorRange(*x), height=350, width=800,
                   toolbar_location=None, tools="", background_fill_color=None)

        p.vbar(x='x', top='counts', width=0.9, source=source, line_color='white',
               fill_color=factor_cmap('x', palette=palette, factors=categories, start=1, end=2))

        p.border_fill_color = None
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.axis.minor_tick_line_color = None
        p.xgrid.grid_line_color = None

        p.xaxis.group_text_color = '#000'
        p.xaxis.group_text_font_size = '10pt'

        legend = self.get_custom_legend(p)
        p.legend.visible = False
        p.add_layout(legend, 'below')

        script, div = components(p)
        return {'script': script, 'div': div}

    def get_content_plot(self, content):
        def get_list_for_plot(category, interactions):
            l = []
            for interaction in ['seen_ads', 'recommended_profiles', 'seen_posts', 'seen_videos']:
                l.append(len(interactions[interaction][category]))
            return l

        interaction_types = [
            'Geschaute Werbung',
            'Vorgeschlagene Profile',
            'Geschaute Posts',
            'Geschaute Videos'
        ]
        categories = ['Parteien', 'Politiker:innen', 'Medien', 'Organisationen', 'andere']
        data = {
            'interactions': interaction_types,
            'Parteien': get_list_for_plot('parties', content),
            'Politiker:innen': get_list_for_plot('politicians', content),
            'Medien': get_list_for_plot('media', content),
            'Organisationen': get_list_for_plot('organisations', content),
            'andere': get_list_for_plot('other', content),
        }

        palette = ['#de0c1c', '#fe2d2d', '#fb7830', '#fecf02', '#ffeea3']

        # this creates [ ("Apples", "2015"), ("Apples", "2016"), ("Apples", "2017"), ("Pears", "2015), ... ]
        x = [(interaction, category) for interaction in interaction_types for category in categories]
        counts = sum(zip(data['Parteien'], data['Politiker:innen'], data['Medien'], data['Organisationen'], data['andere']), ())  # like an hstack

        source = ColumnDataSource(data=dict(x=x, counts=counts))

        p = figure(x_range=FactorRange(*x), height=350, width=800,
                   toolbar_location=None, tools="", background_fill_color=None)

        p.vbar(x='x', top='counts', width=1, source=source, line_color='white',
               fill_color=factor_cmap('x', palette=palette, factors=categories, start=1, end=2))

        p.border_fill_color = None
        p.y_range.start = 0
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None

        p.xaxis.group_text_color = '#000'
        p.xaxis.group_text_font_size = '10pt'

        legend = self.get_custom_legend(p)
        p.legend.visible = False
        p.add_layout(legend, 'below')

        script, div = components(p)
        return {'script': script, 'div': div}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['test'] = self.kwargs['participant_id']
        # data = self.get_data()  TODO: Enable when in production

        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, 'reports/static/temp/politics_data.json')
        with open(file_path, encoding='latin1') as f:
            data = json.load(f)
        context['test_data'] = json.dumps(data).encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')

        # Variables
        donation_instagram = None  # Boolean TODO
        donation_facebook = None  # Boolean TODO

        insta_account_list = self.load_insta_account_list()
        followed_insta_accounts, n_insta_accounts = self.get_follows_insta(data, insta_account_list)
        insta_interactions = self.get_interactions_insta(data, insta_account_list)
        insta_proposed_content = self.get_proposed_content_insta(data, insta_account_list)

        context['n_insta_follows'] = n_insta_accounts

        # Graph 1: n per account category
        context['insta_follows_plot'] = self.get_insta_follows_plot(followed_insta_accounts)

        # Graph 2: account category axis + comparison

        # Graph 3: interaction bar plot per category
        context['insta_interaction_plot'] = self.get_interaction_plot(insta_interactions)

        # Graph 4: proposed content bar plot per category
        context['insta_content_plot'] = self.get_content_plot(insta_proposed_content)

        return context

"""
For console to load xlsx files:
import json
import os

cur_dir = os.path.dirname(os.path.realpath(__file__))
file_path = './ddl/reports/static/temp/media.xlsx'

f = pd.read_excel(os.path.join(cur_dir, path))
f_json = json.loads(f.to_json(orient='records')
"""


# class BaseIndividualReport(DDMReport, DetailView):
#     """ Base class to generate an individual report. """
#     model = Classroom
#     template_name = 'reports/youtube/individual_report.html'
#
#     def setup(self, request, *args, **kwargs):
#         return super().setup(request, *args, **kwargs)
#
#     def get_endpoint(self):
#         return self.object.track.ddm_api_endpoint
#
#     def get_token(self):
#         return self.object.track.ddm_api_token
#
#     def get_payload(self):
#         payload = {'participant_id': self.kwargs.get('participant_id')}
#         return payload
