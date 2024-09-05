import copy
import json
import os

from django.conf import settings


TYPES_DICT_PLACEHOLDER = {
    'media': [],
    'organisation': [],
    'party': [],
    'politician': [],
    'other': []
}


def load_political_account_list():
    """Load list of instagram accounts from static files."""
    path_fb_accounts = os.path.join(settings.BASE_DIR, 'reports/static/reports/data/fb_accounts_complete.json')
    with open(path_fb_accounts) as f:
        accounts = json.load(f)
        accounts = json.loads(json.dumps(accounts).encode('latin1').decode('utf-8'))
    return accounts


def get_follows(data, political_accounts, bp_name='Gefolgte Seiten Facebook'):
    if bp_name not in data:
        return None
    if data[bp_name] is None:
        return None

    followed_accounts = copy.deepcopy(TYPES_DICT_PLACEHOLDER)
    for account in data[bp_name][0]:
        profile = account['string_list_data'][0]['href']  # TODO: Adapt data structure
        if profile in political_accounts.keys():
            fb_profile = political_accounts[profile]
            profile_type = fb_profile['type']
            if profile_type in ['media', 'organisation', 'party', 'politician']:
                followed_accounts[profile_type].append(profile)
        else:
            followed_accounts['other'].append(profile)

    return followed_accounts


def get_n_follows(data, bp_name='Gefolgte Seiten Facebook'):
    return len(data[bp_name][0])  # TODO: Check data structure


def get_interactions(data, political_accounts):
    bp_names = [
        'Gelikete Seiten Facebook', 'Likes Facebook',
        'Kommentare Facebook', 'Story Interaction Facebook'
    ]
    interaction_keys = [  # TODO - Info: Changed keys (compared to insta) - may affect interaction plot
        'likes_pages',
        'likes_general',
        'comments_general',
        'comments_stories'
    ]
    interactions = {key: copy.deepcopy(TYPES_DICT_PLACEHOLDER) for key in interaction_keys}

    for index, bp_name in enumerate(bp_names):
        if bp_name not in data:
            continue
        if data[bp_name] is None:
            continue

        key = interaction_keys[index]
        for account in data[bp_name][0]:
            profile = 'https://www.instagram.com/' + account['title'].strip()  # TODO: Check data structure
            if profile in political_accounts.keys():
                fb_profile = political_accounts[profile]
                profile_type = fb_profile['type']
                if profile_type in ['media', 'organisation', 'party', 'politician']:
                    interactions[key][profile_type].append(profile)
            else:
                interactions[key]['other'].append(profile)

    return interactions


def get_proposed_content(data, political_accounts):
    bp_names = [
        'Kürzlich geschaut Facebook', 'Kürzlich besucht Facebook'
    ]
    content_keys = [  # TODO - Info: Changed keys (compared to insta) - may affect interaction plot
        'seen_posts',
        'seen_videos'
    ]
    content = {key: copy.deepcopy(TYPES_DICT_PLACEHOLDER) for key in content_keys}

    for index, bp_name in enumerate(bp_names):
        if bp_name not in data:
            continue
        if data[bp_name] in [None, []]:
            continue

        key = content_keys[index]
        for account in data[bp_name][0]:
            try:
                profile = 'https://www.instagram.com/' + account['string_map_data']['Author']['value'].strip()  # TODO: Check data structure
            except:
                continue

            if profile in political_accounts.keys():
                fb_profile = political_accounts[profile]
                profile_type = fb_profile['type']
                if profile_type in ['media', 'organisation', 'party', 'politician']:
                    content[key][profile_type].append(profile)
            else:
                content[key]['other'].append(profile)
    return content
