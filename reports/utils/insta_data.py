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


def load_local_example_donation():
    file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/politics_data.json')
    with open(file_path, encoding='latin1') as f:
        data = json.load(f)
    # context['test_data'] = json.dumps(data).encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
    return data


def load_local_example_responses():
    file_path = os.path.join(settings.BASE_DIR, 'reports/static/temp/politics_responses.json')
    with open(file_path, encoding='latin1') as f:
        responses = json.load(f)
    return responses


def load_political_account_list():
    """Load list of instagram accounts from static files."""
    path_insta_accounts = os.path.join(settings.BASE_DIR, 'reports/static/reports/data/insta_accounts_complete.json')
    with open(path_insta_accounts, encoding='latin1') as f:
        insta_accounts = json.load(f)
        insta_accounts = json.loads(json.dumps(insta_accounts).encode('latin1').decode('utf-8'))
    return insta_accounts


def check_if_bps_available(data, bp_list):
    if not any(bp in data.keys() for bp in bp_list):
        return False
    else:
        if not any(data[bp] for bp in bp_list):
            return False
        else:
            return True


def get_n_follows(data, bp_name='Gefolgte Kanäle Instagram'):
    return len(data[bp_name][0])


def get_follows_insta(data, insta_accounts, bp_name='Gefolgte Kanäle Instagram'):  # 'Gefolgte KanÃ¤le Instagram'
    if bp_name not in data:
        return None
    if data[bp_name] is None:
        return None

    followed_accounts = copy.deepcopy(TYPES_DICT_PLACEHOLDER)
    for account in data[bp_name][0]:
        profile = account['string_list_data'][0]['href']
        if profile in insta_accounts.keys():
            insta_profile = insta_accounts[profile]
            profile_type = insta_profile['type']
            if profile_type in ['media', 'organisation', 'party', 'politician']:
                followed_accounts[profile_type].append(profile)
        else:
            followed_accounts['other'].append(profile)

    return followed_accounts


def get_interactions_insta(data, insta_accounts):
    bp_names = [
        'Kommentare Instagram',
        'Reels Kommentare Instagram'
    ]
    interaction_keys = [
        'comments_general',
        'comments_reels'
    ]
    interactions = {key: copy.deepcopy(TYPES_DICT_PLACEHOLDER) for key in interaction_keys}

    for index, bp_name in enumerate(bp_names):
        if bp_name not in data:
            continue
        if data[bp_name] is None:
            continue

        key = interaction_keys[index]
        for account in data[bp_name][0]:
            if bp_name in ['Kommentare Instagram', 'Reels Kommentare Instagram']:
                try:
                    profile = 'https://www.instagram.com/' + account['string_map_data']['Media Owner']['value'].strip()
                except KeyError:
                    continue
            else:
                profile = 'https://www.instagram.com/' + account['title'].strip()
            if profile in insta_accounts.keys():
                insta_profile = insta_accounts[profile]
                profile_type = insta_profile['type']
                if profile_type in ['media', 'organisation', 'party', 'politician']:
                    interactions[key][profile_type].append(profile)
            else:
                interactions[key]['other'].append(profile)

    return interactions


def get_proposed_content_insta(data, insta_accounts):
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
    content = {key: copy.deepcopy(TYPES_DICT_PLACEHOLDER) for key in content_keys}

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
                profile_type = insta_profile['type']
                if profile_type in ['media', 'organisation', 'party', 'politician']:
                    content[key][profile_type].append(profile)
            else:
                content[key]['other'].append(profile)
    return content
