from .plots.facebook import load_facebook_statistics
from .plots.instagram import load_instagram_statistics


def update_instagram_statistics():
    instagram_statistics = load_instagram_statistics()
    instagram_statistics.update_statistics()
    return


def update_facebook_statistics():
    facebook_statistics = load_facebook_statistics()
    facebook_statistics.update_statistics()
    return
