from django import template
from mainpage.models import Footer

register = template.Library()


# Footer snippet
@register.inclusion_tag('mainpage/footer/custom_footer.html', takes_context=True)
def footer(context):
    return {
        'footer': Footer.objects.first(),
        'request': context['request'],
    }
