from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'ddl/base.html'


class VPStudyLandingPage(TemplateView):
    template_name = 'ddl/vp_study_landing.html'


class VPStudyLandingPageInvited(TemplateView):
    template_name = 'ddl/vp_study_landing_invited.html'
