import os
import re

from django.conf import settings
from langdetect import detect, LangDetectException  # TODO: May need to be added to requirements


def get_searches_by_language(search_queries, min_words_per_search=1):
    """
    Extract the titles of the searches and group them by language.
    A search is only considered if it has at least min_words_per_search words.
    """
    languages = {'uk': 'Ukrainian', 'en': 'English', 'de': 'German'}
    titles_by_lang = {language: "" for language in languages.values()}
    n_per_lang = {'uk': 0, 'en': 0, 'de': 0, 'unidentified': 0}
    for query in search_queries:
        if len(query.split()) < min_words_per_search:
            continue
        try:
            lang = detect(query)
        except LangDetectException:
            continue

        if lang in languages:
            titles_by_lang[languages[lang]] += query + " "
            n_per_lang[lang] += 1
        else:
            n_per_lang['unidentified'] += 1
    return titles_by_lang, n_per_lang


def parse_dictionary(dictionary_path, categories=None):
    """
    Parse the dictionary file and return the categories and patterns indexing.
    """
    try: 
        with open(dictionary_path, encoding='utf8') as f:
            dictionary = f.read()
    except:
        with open(dictionary_path, encoding='latin1') as f:
            dictionary = f.read()
    dictionary = dictionary.split('\n')

    # extract categories indexing
    for i, line in enumerate(dictionary[1:]):
        if line == "%":
            break 
    idx_to_categories = dictionary[1:i+1]
    idx_to_categories = {category.split('\t')[0]: category.split('\t')[1] for category in idx_to_categories}
    if categories:
        idx_to_categories = {k: v for k, v in idx_to_categories.items() if v in categories}

    # extract patterns indexing
    pattern_to_idx = dictionary[i+2:]
    pattern_to_idx = {pattern.split('\t')[0]: pattern.split('\t')[1:] for pattern in pattern_to_idx}
    if categories:
        filtered_pattern_to_idx = {}
        for pattern, idxs in pattern_to_idx.items():
            filtered_pattern_to_idx[pattern] = [idx for idx in idxs if idx in idx_to_categories]
            if filtered_pattern_to_idx[pattern] == []:
                del filtered_pattern_to_idx[pattern]
        pattern_to_idx = filtered_pattern_to_idx

    return idx_to_categories, pattern_to_idx


def tokenize(text):
    """Tokenize the text considering only words."""
    return re.findall(r'\b\w+\b', text.lower())


def get_scores(text, idx_to_categories, pattern_to_idx):
    """Calculate the scores of the categories for the given text."""
    tokens = tokenize(text)
    n_words = len(tokens)
    if n_words == 0:
        return None
    categories = {category: 0 for category in idx_to_categories.values()}
    for token in tokens:
        for pattern, idxs in pattern_to_idx.items():
            if pattern[-1] == "*":
                pattern = pattern[:-1]
                if token.startswith(pattern):
                    for idx in idxs:
                        categories[idx_to_categories[idx]] += (1 / n_words) * 100
            else:
                if token == pattern:
                    for idx in idxs:
                        categories[idx_to_categories[idx]] += (1 / n_words) * 100
    return categories


def transform_json_to_tabular(json_data):
    """Transform the json data to a tabular format. Done to facilitate R reading."""
    tabular_data = []
    for language, emotions in json_data.items():
        row = {"language": language}
        row.update(emotions)
        tabular_data.append(row)
    return tabular_data


def get_scores_by_language(titles_by_lang, dictionary_folder, categories=None):
    """Calculate the scores of the categories for the given texts in the different languages."""
    scores_by_lang = {lang: {} for lang in titles_by_lang}
    for lang, text in titles_by_lang.items():
        idx_to_categories, pattern_to_idx = parse_dictionary(dictionary_folder + lang + '.dic', categories=categories)
        scores = get_scores(text, idx_to_categories, pattern_to_idx)
        if scores:
            scores_by_lang[lang] = scores
    return scores_by_lang  # transform_json_to_tabular(scores_by_lang)


def get_scores_for_report(search_queries):
    """Main function to calculate the scores of the categories for the searches in the browser history."""
    dictionary_path = os.path.join(settings.BASE_DIR, 'reports/static/reports/dicts/')
    categories = [
        "posemo",
        "negemo",
        "anx",
        "anger",
        "sad",
        "social",
        "cogproc",
        "bio",
        "body",
        "wc"
    ]
    max_number_of_searches = 1000
    if len(search_queries) > max_number_of_searches:
        search_queries = search_queries[:max_number_of_searches]

    # min_words_per_search = 4
    titles_by_lang, n_per_lang = get_searches_by_language(search_queries)  #, min_words_per_search=min_words_per_search)
    scores = get_scores_by_language(titles_by_lang, dictionary_path, categories=categories)
    return scores, n_per_lang
