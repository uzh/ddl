import re
from dateutil.parser import parse


def get_clean_search_events(event_list):
    """Takes a list of events and only keeps search request events."""
    # Identify searches
    search_keys = ['^Gesucht nach: ', '^Searched for ', '^Vous avez recherché ', '^Hai cercato ']
    search_re = '|'.join(search_keys)
    search_events = [e for e in event_list if re.search(search_re, e['title'])]
    for event in search_events:
        event['title'] = re.sub(search_re, '', event['title'])
        event['time'] = parse(event['time'])
    return search_events


def get_clean_click_events(event_list):
    """
    Takes a list of events and only keeps clicked search result events.
    Event strings are also cleaned (e.g., automatic pre-/postfixes added by Google
    are removed).
    """
    click_keys = [' aufgerufen$', '^Visited ', '^Vous avez consulté ', '^Hai visitato ']
    click_re = '|'.join(click_keys)
    click_events = [e for e in event_list if re.search(click_re, e['title'])]

    for event in click_events:
        event['title'] = re.sub(click_re, '', event['title'])
        event['time'] = parse(event['time'])
    return click_events
