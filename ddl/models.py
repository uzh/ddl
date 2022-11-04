from ckeditor.fields import RichTextField

from django.contrib.auth.models import AbstractUser
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail import fields
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, FieldRowPanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.models import register_snippet


# CUSTOM USER MODEL
# ------------------------------------------------------------------------------
class User(AbstractUser):
    pass


# WAGTAIL MODELS
# ------------------------------------------------------------------------------
class HighlightBlock(blocks.StructBlock):
    title = blocks.RichTextBlock()
    text = blocks.RichTextBlock()
    background = ImageChooserBlock(required=False)
    alignment = blocks.ChoiceBlock(choices=[
        ('left', 'left'),
        ('right', 'right'),
    ])

    class Meta:
        icon = 'pick'
        template = 'ddl/components/highlight_block.html'


class BasicPage(Page):
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="full title", icon='title')),
        ('paragraph', blocks.RichTextBlock(icon='pilcrow')),
        ('list', blocks.ListBlock(blocks.CharBlock(label="List"), icon='list-ul')),
        ('image', ImageChooserBlock()),
        ('highlight', HighlightBlock()),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body', classname='full'),
    ]


# BLOG
# ------------------------------------------------------------------------------
class BlogPage(Page):
    template = 'ddl/blog/blog_page.html'

    sub_title = models.CharField(max_length=100, blank=True)
    teaser = models.TextField(max_length=250, blank=True)

    body = StreamField([
        ('text', blocks.RichTextBlock(icon='pilcrow')),
        ('image', ImageChooserBlock()),
    ], use_json_field=True, blank=True)
    date = models.DateField()

    author = models.CharField(max_length=100, blank=True)
    author_email = models.EmailField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('sub_title'),
        FieldPanel('teaser'),
        FieldPanel('body'),
        FieldPanel('date'),
        MultiFieldPanel([FieldPanel('author'), FieldPanel('author_email')], heading='Author Information')
    ]

    parent_page_types = ['BlogIndexPage']


class BlogIndexPage(Page):
    template = 'ddl/blog/blog_index.html'
    intro = fields.RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro', classname='full')
    ]

    subpage_types = ['BlogPage']

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Add extra variables and return the updated context
        context['blog_posts'] = BlogPage.objects.child_of(self).live().order_by('-date')
        return context


# FORMS
# ------------------------------------------------------------------------------
class FormField(AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')


class FormPage(AbstractEmailForm):
    template = 'ddl/forms/basic_form_page.html'
    landing_page_template = 'ddl/forms/basic_landing_page.html'

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)
    submit_label = models.CharField(max_length=100)

    content_panels = AbstractEmailForm.content_panels + [
        FormSubmissionsPanel(),
        FieldPanel('intro', classname="full"),
        InlinePanel('form_fields', label="Form fields"),
        FieldPanel('submit_label', classname="full"),
        FieldPanel('thank_you_text', classname="full"),
        MultiFieldPanel([
            FieldRowPanel([
                FieldPanel('from_address', classname="col6"),
                FieldPanel('to_address', classname="col6"),
            ]),
            FieldPanel('subject'),
        ], "Email"),
    ]


# SNIPPETS
# ------------------------------------------------------------------------------
@register_snippet
class Footer(models.Model):
    text = RichTextField()

    panels = [
        FieldPanel('text'),
    ]

    def __str__(self):
        return self.text
