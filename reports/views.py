import pandas as pd
import pytz
import requests

from datetime import timedelta, datetime

from ddm.participation.models import Participant
from django.conf import settings
from django.views.generic import TemplateView
from requests import JSONDecodeError

from .plots import youtube as yt_plots
from .plots import search as search_plots
from .plots import chatgpt as gpt_plots
from .utils.get_scores import get_scores_for_report
from .utils import yt_data, search_data


utc = pytz.UTC


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


class SearchReport(BaseReport, TemplateView):
    template_name = 'reports/search.html'
    project_pk = settings.SEARCH_PROJECT_PK
    token = settings.SEARCH_API_KEY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status'] = 'okay'
        donation = self.get_donation_context(context)

        if 'Google Suchverlauf' not in donation.keys():
            context['status'] = 'Etwas ist schiefgelaufen und der Report konnte nicht generiert werden.'
            return context

        if not donation['Google Suchverlauf']:
            context['status'] = 'Etwas ist schiefgelaufen und der Report konnte nicht generiert werden.'
            return context

        events = donation['Google Suchverlauf'][0]

        searches = search_data.get_clean_search_events(events)
        search_dates = [e['time'] for e in searches]
        search_date_max = max(search_dates)
        search_date_min = search_date_max - timedelta(days=30)
        context['search_date_max'] = search_date_max
        context['search_date_min'] = search_date_min

        searches_last_30_days = [e['title'] for e in searches if e['time'] >= search_date_min]
        context['n_searches'] = len(searches_last_30_days)

        scores, n_per_lang = get_scores_for_report(searches_last_30_days)
        context['scores'] = scores
        context['n_queries_de'] = n_per_lang['de']
        context['n_queries_en'] = n_per_lang['en']
        context['n_queries_uk'] = n_per_lang['uk']
        context['n_queries_unidentified'] = n_per_lang['unidentified']
        context['n_queries_total'] = sum(n_per_lang.values())

        clicks = search_data.get_clean_click_events(events)
        clicks_last_30_days = [e for e in clicks if e['time'] >= search_date_min]
        clicks_titles = [e['title'] for e in clicks]
        context['n_clicks'] = len(clicks_last_30_days)
        context['clicks'] = clicks_titles

        n_langs_with_score = 0
        if scores['German']:
            context['plot_de'] = search_plots.get_language_plot(scores['German'], bar_color='#FF0000')
            n_langs_with_score += 1

        if scores['English']:
            context['plot_en'] = search_plots.get_language_plot(scores['English'], bar_color='#00247D')
            n_langs_with_score += 1

        if scores['Ukrainian']:
            context['plot_ukr'] = search_plots.get_language_plot(scores['Ukrainian'], bar_color='#0057b8')
            n_langs_with_score += 1

        context['n_langs_with_score'] = n_langs_with_score
        context['test_data'] = donation['Google Suchverlauf'][0]
        return context

    def get_donation_context(self, context):
        data = self.get_data()

        # For local testing:
        # file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/search_donation.json')
        # with open(file_path, encoding='latin1') as f:
        #     data = json.loads(f.read())
        return data


class DigitalMealReport(BaseReport, TemplateView):  # BaseIndividualReport,
    template_name = 'reports/digital_meal.html'
    project_pk = settings.DIGITALMEAL_PROJECT_PK
    token = settings.DIGITALMEAL_API_KEY

    def get_endpoint(self):
        url = self.object.track.data_endpoint
        url = url.replace('class-data', 'individual-data')
        return url

    def get_participation_date(self):
        participant_id = self.kwargs.get('participant_id')
        participant = Participant.objects.filter(external_id=participant_id)
        if not participant:
            participation_date = None
        else:
            participation_date = participant[0].end_time.replace(tzinfo=utc)
        return participation_date

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.get_data()  # json.load(self.get_data())
        context['status'] = 'okay'

        # Watch history
        watch_history_available = True
        watch_history_id = 'Angesehene Videos'
        if watch_history_id in data.keys():
            if data[watch_history_id]:
                context.update(self.get_watch_context(data[watch_history_id][0]))
            else:
                watch_history_available = False
        else:
            watch_history_available = False

        # Search history (sh)
        search_history_available = True
        search_history_id = 'Suchverlauf'
        if search_history_id in data.keys():
            if data[search_history_id]:
                context.update(self.get_search_context(data[search_history_id][0]))
            else:
                search_history_available = False
        else:
            search_history_available = False

        if not watch_history_available and not search_history_available:
            context['status'] = 'error'
        return context

    def get_watch_context(self, data):
        c = {}  # c = context
        if not data:
            c['wh_available'] = False
            return c
        c['wh_available'] = True

        wh = yt_data.exclude_google_ads_videos(data)
        wh_ids = yt_data.get_video_ids(wh)

        wh_dates = yt_data.get_date_list(wh)
        self.add_date_infos_to_context(c, wh_dates, 'wh')
        self.add_wh_statistics_to_context(c, wh, wh_ids)
        self.add_favorite_videos_to_context(c, wh, wh_ids)
        self.add_wh_timeseries_plots_to_context(c, [wh_dates], c['wh_dates_min'], c['wh_dates_max'])
        self.add_wh_plots_to_context(c, wh_dates)

        # Watched channels
        channels = yt_data.get_channels_from_history(wh)
        self.add_wh_channel_info_to_context(c, channels)
        return c

    def get_search_context(self, data):
        c = {}  # c = context
        if not data:
            c['search_available'] = False
            return c
        c['search_available'] = True

        sh = yt_data.exclude_ads_from_search_history(data)
        sh = yt_data.clean_search_titles(sh)
        sh_dates = yt_data.get_date_list(sh)
        self.add_date_infos_to_context(c, sh_dates, 'sh')
        self.add_sh_statistics_to_context(c, sh)
        search_terms = [t['title'] for t in sh]

        self.add_sh_plot_to_context(c, search_terms)
        return c

    @staticmethod
    def add_wh_timeseries_plots_to_context(context, date_list, min_date, max_date):
        dates_days = yt_data.get_summary_counts_per_date(date_list, 'd', 'mean')
        context['dates_plot_days'] = yt_plots.get_timeseries_plot(
            pd.Series(dates_days), date_min=min_date, date_max=max_date)

        dates_weeks = yt_data.get_summary_counts_per_date(date_list, 'w', 'mean')
        context['dates_plot_weeks'] = yt_plots.get_timeseries_plot(
            pd.Series(dates_weeks), bin_width=7, date_min=min_date, date_max=max_date)

        dates_months = yt_data.get_summary_counts_per_date(date_list, 'w', 'mean')
        context['dates_plot_months'] = yt_plots.get_timeseries_plot(
            pd.Series(dates_months), bin_width=30, date_min=min_date, date_max=max_date)

        dates_years = yt_data.get_summary_counts_per_date(date_list, 'y', 'mean')
        context['dates_plot_years'] = yt_plots.get_timeseries_plot(
            pd.Series(dates_years), bin_width=365, date_min=min_date, date_max=max_date)
        return context

    @staticmethod
    def add_date_infos_to_context(context, date_list, prefix):
        context[f'{prefix}_dates_min'] = min(date_list)
        context[f'{prefix}_dates_max'] = max(date_list)
        context[f'{prefix}_date_range'] = max(date_list) - min(date_list)
        return context

    @staticmethod
    def add_favorite_videos_to_context(context, watch_history, video_ids):
        video_titles = yt_data.get_video_title_dict(watch_history)
        most_popular_videos = pd.Series(video_ids).value_counts()[:10].to_dict()
        videos_top_ten = []
        for key, value in most_popular_videos.items():
            videos_top_ten.append({
                'id': key,
                'count': value,
                'title': yt_data.clean_video_title(video_titles.get(key))
            })
        context['fav_vids_top_ten'] = videos_top_ten
        return context

    def add_wh_statistics_to_context(self, context, watch_history, video_ids):
        # Statistics overall
        context['n_vids_overall'] = len(watch_history)
        context['n_vids_unique_overall'] = len(set(video_ids))
        context['n_vids_per_day'] = round((len(watch_history) / context['wh_date_range'].days), 2)

        # Statistics interval
        #interval_min, interval_max = context['wh_dates_min'], context['wh_dates_max']
        interval_max = self.get_participation_date()
        if not interval_max:
            interval_max = datetime.today().replace(tzinfo=utc)
        interval_min = interval_max - timedelta(days=30)
        interval_min = interval_min.replace(tzinfo=utc)

        context['wh_int_min_date'] = interval_min
        context['wh_int_max_date'] = interval_max
        wh_interval = yt_data.get_entries_in_date_range(
            watch_history, interval_min, interval_max)
        wh_interval_ids = yt_data.get_video_ids(wh_interval)
        context['n_vids_interval'] = len(wh_interval)
        context['n_vids_unique_interval'] = len(set(wh_interval_ids))
        context['n_vids_mean_interval'] = len(wh_interval) / 30
        return context

    @staticmethod
    def add_wh_plots_to_context(context, date_list):
        context['weekday_use_plot'] = yt_plots.get_weekday_use_plot(date_list)
        context['hours_plot'] = yt_plots.get_day_usetime_plot(date_list)
        return context

    @staticmethod
    def add_wh_channel_info_to_context(context, channels, channels_for_plot=None):
        if channels_for_plot is None:
            channels_for_plot = channels
        context['channel_plot'] = yt_plots.get_channel_plot(channels_for_plot)
        context['n_distinct_channels'] = len(set(channels))
        return context

    def add_sh_statistics_to_context(self, context, search_history, n_donations=1):
        # Statistics overall
        context['n_searches_overall'] = len(search_history)
        context['n_searches_mean_overall'] = len(search_history) / n_donations

        # Statistics interval
        interval_min, interval_max = context['sh_dates_min'], context['sh_dates_max']
        context['sh_int_min_date'] = interval_min
        context['sh_int_max_date'] = interval_max
        sh_interval = yt_data.get_entries_in_date_range(search_history, interval_min, interval_max)
        context['n_search_interval'] = len(sh_interval)
        context['n_search_mean_interval'] = len(sh_interval) / n_donations
        return context

    @staticmethod
    def add_sh_plot_to_context(context, search_terms):
        context['search_plot'] = yt_plots.get_searches_plot(search_terms)
        return context


class ChatGPTReport(BaseReport, TemplateView):
    template_name = 'reports/chatgpt.html'
    project_pk = settings.CHATGPT_PROJECT_PK
    token = settings.CHATGPT_API_KEY

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = self.add_response_context(context)
        context['status'] = 'okay'
        return context

    def add_response_context(self, context):
        """Get context variables from questionnaire responses."""
        responses_api = self.get_responses()

        if not responses_api:
            context['status'] = 'not okay'
            return context

        responses = responses_api['responses'][0]
        context['responses'] = responses['response_data']
        variables = [
            'trust-chatgpt',
            'trust-science',
            'benefit-chatgpt-1',
            'benefit-chatgpt-2',
            'benefit-chatgpt-3',
            'risk-chatgpt-1',
            'risk-chatgpt-2',
            'risk-chatgpt-3'
        ]

        for variable in variables:
            response = responses[variable]
            plot_name = variable.replace('-', '_') + '_plot'
            context[plot_name] = gpt_plots.get_bar_plot(variable, response)

        try:
            use_response = responses['use-chatgpt']
            age_group = responses['age']
            if age_group in ['1', '2', '3', '4', '5'] and use_response in ['1', '2', '3', '4', '5']:
                cell_highlight = age_group + '-' + use_response
                context['highlight'] = cell_highlight
        except ValueError:
            pass

        return context
