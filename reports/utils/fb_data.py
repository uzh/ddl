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


def check_if_bps_available(data, bp_list):
    if not any(bp in data.keys() for bp in bp_list):
        return False
    else:
        if not any(data[bp] for bp in bp_list):
            return False
        else:
            return True


def get_follows(data, political_accounts, bp_name='Gefolgte Personen Facebook'):
    if bp_name not in data:
        return None
    if data[bp_name] is None:
        return None

    followed_accounts = copy.deepcopy(TYPES_DICT_PLACEHOLDER)
    for account in data[bp_name][0]:
        profile = account['name'].encode('latin-1').decode('utf-8')
        if profile in political_accounts.keys():
            fb_profile = political_accounts[profile]
            profile_type = fb_profile['type']
            if profile_type in ['media', 'organisation', 'party', 'politician']:
                followed_accounts[profile_type].append(profile)
        else:
            followed_accounts['other'].append(profile)

    return followed_accounts


def get_n_follows(data, bp_name='Gefolgte Personen Facebook'):
    return len(data[bp_name][0])


def get_interactions(data, political_accounts):
    bp_names = [
        'Likes Facebook', 'Kommentare Facebook', 'Story Interaction Facebook'
    ]
    """
    'Likes Facebook': [[{'title': "Nico Pfiffner liked SP Schweiz's post.", 'timestamp': 1725527135}]],
    'Kommentare Facebook': [[]],
    'Story Interaction Facebook': [[]]
    """
    interaction_keys = [  # TODO - Info: Changed keys (compared to insta) - may affect interaction plot
        'likes',
        'comments',
        'story_interactions'
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
    bp_name = 'Kürzlich besucht Facebook'  # 'Kürzlich geschaut Facebook',
    content = copy.deepcopy(TYPES_DICT_PLACEHOLDER)

    if bp_name not in data:
        return content
    if data[bp_name] in [None, []]:
        return content

    for d in data[bp_name][0]:
        if 'name' not in d.keys() or 'entries' not in d.keys():
            continue
        if d['name'] != 'Profile visits':
            continue
        if not d['entries']:
            return content

        for e in d['entries']:
            try:
                profile = e['data']['name'].encode('latin-1').decode('utf-8')
            except:
                continue
            if profile in political_accounts.keys():
                fb_profile = political_accounts[profile]
                profile_type = fb_profile['type']
                if profile_type in ['media', 'organisation', 'party', 'politician']:
                    content[profile_type].append(profile)
            else:
                content['other'].append(profile)
    return content
