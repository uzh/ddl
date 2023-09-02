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

    @staticmethod
    def get_response_data(project_id, participant_id):
        """
        Gets a participant's questionnaire answers by querying from the DDM API.

        Passes the 'project id' and the 'external participant id'
        as query parameters.
        """
        api_endpoint = f'{settings.DDM_BASE_URL}api/project/{project_id}/responses'
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

        if donated_data:
            watch_history = donated_data.get(settings.DDM_WATCH_BP_ID, None)
            search_history = donated_data.get(settings.DDM_SEARCH_BP_ID, None)
        else:
            watch_history = None
            search_history = None

        # 2) get and transform all data series
        if watch_history:
            if len(watch_history[0]) > 0:
                watched_videos, seen_ads = yt_data.separate_videos_and_ads(watch_history[0])
                dates = yt_data.get_date_list(watched_videos)
                date_range = max(dates) - min(dates)
                n_videos_total = len(watched_videos)

                fav_video = yt_data.get_most_watched_video(watched_videos)
                video_titles = yt_data.get_video_title_dict(watched_videos)
                fav_video['title'] = video_titles.get(fav_video['id'])

                channels = yt_data.get_channels_from_history(watched_videos)
                try:
                    n_videos_jun_to_aug = yt_data.filter_jun_to_aug(watched_videos).shape[0]
                except:
                    n_videos_jun_to_aug = None

                try:
                    n_ads_jun_to_aug = yt_data.filter_jun_to_aug(seen_ads).shape[0]
                except:
                    n_ads_jun_to_aug = None

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
            else:
                context.update({
                    'dates_plot': None,
                    'weekday_use_plot': None,
                    'hours_plot': None,
                    'channel_plot': None,
                    'n_distinct_channels': None,
                    'date_first': None,
                    'date_last': None,
                    'n_videos_mean': None,
                    'n_videos_total': None,
                    'fav_video': None
                })
                n_videos_jun_to_aug = None
                n_ads_jun_to_aug = None
        else:
            n_videos_jun_to_aug = None
            n_ads_jun_to_aug = None

        if search_history:
            search_history = search_history[0]

            if len(search_history) > 0:
                search_dates = yt_data.get_date_list(search_history)
                search_terms = yt_data.get_search_term_frequency(search_history, 15)

                context.update({
                    'date_first_search': min(search_dates),
                    'n_searches': len(search_history),
                    'searches': search_terms,
                    'search_plot': yt_plots.get_searches_plot(search_history)
                })

            else:
                context.update({
                    'date_first_search': None,
                    'n_searches': None,
                    'searches': None,
                    'search_plot': None
                })

        responses = self.get_response_data(project_id, participant_id)
        if responses:
            responses = responses[0]
        else:
            responses = {}

        videos_seen_estimate = responses.get('videos_seen_est', None)
        ads_seen_estimate = responses.get('ads_seen_est', None)

        if None not in (videos_seen_estimate, n_videos_jun_to_aug):
            video_estimate_available = True
        else:
            video_estimate_available = False

        if None not in (ads_seen_estimate, n_ads_jun_to_aug):
            ad_estimate_available = True
        else:
            ad_estimate_available = False

        context.update({
            'videos_seen_estimate': videos_seen_estimate,
            'ads_seen_estimate': ads_seen_estimate,
            'video_estimate_available': video_estimate_available,
            'ad_estimate_available': ad_estimate_available,
            'n_videos_jun_to_aug': n_videos_jun_to_aug,
            'n_ads_jun_to_aug': n_ads_jun_to_aug
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

        if donated_data:

            data_lightly_active = donated_data['Minuten leichte Aktivität'][0]
            if data_lightly_active:
                data_lightly_active = pd.DataFrame.from_dict(data_lightly_active)
            else:
                data_lightly_active = None

            data_moderately_active = donated_data['Minuten moderate Aktivität'][0]
            if data_moderately_active:
                data_moderately_active = pd.DataFrame.from_dict(data_moderately_active)
            else:
                data_moderately_active = None

            data_very_active = donated_data['Minuten hohe Aktivität'][0]
            if data_very_active:
                data_very_active = pd.DataFrame.from_dict(data_very_active)
            else:
                data_very_active = None

            try:
                activity_plot, act_date_min, act_date_max = fitbit_plots.get_active_minutes_plot(
                    data_lightly_active,
                    data_moderately_active,
                    data_very_active
                )
            except:
                activity_plot = None
                act_date_min = None
                act_date_max = None

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

            try:
                steps_plot = fitbit_plots.get_steps_plot(data_steps)
            except:
                steps_plot = None

            # 3) add to context
            context.update({
                'data': donated_data,
                'activity_plot': activity_plot,
                'activity_date_min': act_date_min,
                'activity_date_max': act_date_max,
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
