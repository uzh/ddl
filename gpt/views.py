from ddm.participation.views import BriefingView, DataDonationView


class BriefingViewGPT(BriefingView):
    step_name = 'briefing-gpt'
    # Different URL; otherwise can probably stay the same?
    steps = [
        'briefing-gpt',
        'data-donation-gpt',
        'questionnaire',
        'debriefing'
    ]
    pass


class DataDonationViewGPT(DataDonationView):
    template_name = 'gpt/gpt_donation.html'
    step_name = 'data-donation-gpt'
    steps = [
        'briefing-gpt',
        'data-donation-gpt',
        'questionnaire',
        'debriefing'
    ]
    pass
