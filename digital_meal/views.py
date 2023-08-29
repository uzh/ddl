import pandas as pd
import requests

from django.conf import settings
from django.views.generic import TemplateView

from digital_meal.utils import yt_data, yt_plots, fitbit_plots


class IndividualReport(TemplateView):
    """ Generates an individual report. """
    template_name = 'digital_meal/individual_report.html'

    @staticmethod
    def get_data(project_id, participant_id):
        """
        Gets a participant's data by querying from the DDM API.

        Passes the 'project id' and the 'external participant id'
        as query parameters.
        """
        api_endpoint = f'{settings.DDM_BASE_URL}api/project/{project_id}/donations'
        api_token = settings.DDM_API_TOKEN

        headers = {
            'Authorization': f'Token {api_token}'
        }
        payload = {
            'participants': participant_id
        }
        r = requests.get(api_endpoint, headers=headers, params=payload)

        if r.ok:
            return r.json()
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1) get data from api
        participant_id = self.kwargs['external_participant_id']
        project_id = settings.DDM_PROJECT_ID

        donated_data = self.get_data(project_id, participant_id)

        watch_history = donated_data.get(settings.DDM_WATCH_BP_ID, None)
        search_history = donated_data.get(settings.DDM_SEARCH_BP_ID, None)

        # 2) get and transform all data series
        if watch_history:
            watched_videos = yt_data.exclude_google_ads_videos(watch_history[0])
            dates = yt_data.get_date_list(watched_videos)
            date_range = max(dates) - min(dates)
            n_videos_total = len(watched_videos)

            fav_video = yt_data.get_most_watched_video(watched_videos)
            video_titles = yt_data.get_video_title_dict(watched_videos)
            fav_video['title'] = video_titles.get(fav_video['id'])

            channels = yt_data.get_channels_from_history(watched_videos)

            context.update({
                'dates_plot': yt_plots.get_timeseries_plot(dates),
                'weekday_use_plot': yt_plots.get_weekday_use_plot(dates),
                'hours_plot': yt_plots.get_day_usetime_plot(dates),
                'channel_plot': yt_plots.get_channel_plot(channels),
                'n_distinct_channels': len(set(channels)),
                'date_first': min(dates),
                'date_last': max(dates),
                'n_videos_mean': round((n_videos_total / date_range.days), 2),
                'n_videos_total': n_videos_total,
                'fav_video': fav_video
            })

        if search_history:
            search_history = search_history[0]
            search_dates = yt_data.get_date_list(search_history)
            search_terms = yt_data.get_search_term_frequency(search_history, 15)

            context.update({
                'date_first_search': min(search_dates),
                'n_searches': len(search_history),
                'searches': search_terms,
                'search_plot': yt_plots.get_searches_plot(search_history),
                'n_videos_liked': 0,
                'share_videos_liked': 0
            })

        # 3) add to context
        context.update({
            'n_videos_liked': 0,
            'share_videos_liked': 0
        })
        return context


class IndividualFitbitReport(TemplateView):
    """ Generates an individual report. """
    template_name = 'digital_meal/individual_fitbit_report.html'

    @staticmethod
    def get_donation_data(project_id, participant_id, blueprint_id):
        """
        Gets participation data by querying the participation API endpoint of a
        DDM instance that has ddm-pooled enabled.

        Passes the 'external pool project id', the 'external pool participant id'
        and a blueprint id as query parameters.
        """
        api_endpoint = f'{settings.DDM_BASE_URL}api/project/{project_id}/donations'
        api_token = settings.DDM_FITBIT_API_TOKEN

        headers = {
            'Authorization': f'Token {api_token}'
        }
        payload = {
            'participants': participant_id
        }
        r = requests.get(api_endpoint, headers=headers, params=payload)

        if r.ok:
            return r.json()
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1) get data from api
        participant_id = self.kwargs['external_participant_id']
        project_id = settings.DDM_FITBIT_PROJECT_ID
        donated_data = self.get_donation_data(
            project_id, participant_id, blueprint_id=32)

        data_lightly_active = donated_data.get('Minuten leichte Aktivität', None)
        if data_lightly_active:
            data_lightly_active = pd.DataFrame.from_dict(data_lightly_active[0])

            activity_date_min = data_lightly_active.dateTime.min()
            activity_date_max = data_lightly_active.dateTime.max()
        else:
            activity_date_min = None
            activity_date_max = None

        data_moderately_active = donated_data.get('Minuten moderate Aktivität', None)
        if data_moderately_active:
            data_moderately_active = pd.DataFrame.from_dict(data_moderately_active[0])
        data_very_active = donated_data.get('Minuten hohe Aktivität', None)
        if data_very_active:
            data_very_active = pd.DataFrame.from_dict(data_very_active[0])

        try:
            activity_plot = fitbit_plots.get_active_minutes_plot(data_lightly_active, data_moderately_active, data_very_active)
        except:
            activity_plot = None

        # Schlafdaten
        data_sleep = donated_data.get('Schlafdaten', None)
        if data_sleep:
            data_sleep = pd.DataFrame.from_dict(data_sleep[0])
        try:
            sleep_plot = fitbit_plots.get_sleep_plot(data_sleep)
        except:
            sleep_plot = None

        try:
            sleep_pulse_plot = fitbit_plots.get_heart_rate_sleep_plot(data_sleep)
        except:
            sleep_pulse_plot = None

        # Schrittdaten
        data_steps = donated_data.get('Schritte', None)
        if data_steps:
            data_steps = pd.DataFrame.from_dict(data_steps[0])

        steps_plot = fitbit_plots.get_steps_plot(data_steps)

        # 3) add to context
        context.update({
            'data': donated_data,
            'activity_plot': activity_plot,
            'activity_date_min': activity_date_min,
            'activity_date_max': activity_date_max,
            'sleep_plot': sleep_plot,
            'sleep_data': data_sleep,
            'sleep_pulse_plot': sleep_pulse_plot,
            'steps_plot': steps_plot
        })
        return context


class ScientificaLandingView(TemplateView):
    template_name = 'digital_meal/scientifica_landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ddm_url'] = settings.DDM_BASE_URL
        return context
