from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import HighlightBox


@plugin_pool.register_plugin
class HighlightSection(CMSPluginBase):
    model = HighlightBox
    render_template = "mainpage/cms/plugins/highlight_box.html"
    cache = False
