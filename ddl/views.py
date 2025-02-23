from django.shortcuts import render
from django.views.generic import TemplateView


class MainView(TemplateView):
    template_name = 'ddl/base.html'


def custom_404_view(request, exception):
    """ Returns a custom 404 page. """
    return render(request, 'ddl/404.html', status=404)


def custom_500_view(request):
    """ Returns a custom 500 page. """
    return render(request, 'ddl/500.html', status=500)
