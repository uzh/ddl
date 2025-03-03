from ddm.participation.views import BriefingView, DataDonationView


class BriefingViewGPT(BriefingView):
    """
    Overwrite the first two steps to customize the participation flow for
    ChatGPT projects.
    """
    step_name = 'briefing-gpt'
    # Different URL; otherwise can probably stay the same?
    steps = [
        'briefing-gpt',
        'data-donation-gpt',
        'ddm_participation:questionnaire',
        'ddm_participation:debriefing'
    ]
    pass


class DataDonationViewGPT(DataDonationView):
    """
    Overwrite the first two steps to customize the participation flow for
    ChatGPT projects.
    """
    template_name = 'gpt/gpt_donation.html'
    step_name = 'data-donation-gpt'
    steps = [
        'briefing-gpt',
        'data-donation-gpt',
        'ddm_participation:questionnaire',
        'ddm_participation:debriefing'
    ]
    pass
