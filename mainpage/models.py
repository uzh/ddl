from cms.models.pluginmodel import CMSPlugin

from filer.fields.image import FilerImageField

from django.db import models

from djangocms_text_ckeditor.fields import HTMLField


class HighlightBox(CMSPlugin):
    title = models.TextField(default='')
    text = HTMLField(blank=True)
    background = FilerImageField(
        null=True,
        blank=True,
        related_name='background_image',
        on_delete=models.SET_NULL
    )

    ALIGN_CHOICES = (
        ('none', 'none'),
        ('right', 'right'),
        ('left', 'left'),
    )
    alignment = models.CharField(
        max_length=10,
        choices=ALIGN_CHOICES,
        default='none'
    )
