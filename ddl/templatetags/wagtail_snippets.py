from django import template
from ddl.models import Footer

register = template.Library()


# Footer snippet
@register.inclusion_tag('ddl/footer/custom_footer.html',
                        takes_context=True)
def footer(context):
    return {
        'footer': Footer.objects.first(),
        'request': context['request'],
    }
