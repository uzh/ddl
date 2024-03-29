# Generated by Django 3.2.13 on 2023-06-20 14:57

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_pooled', '0004_pooledproject_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pooledproject',
            name='donation_briefing',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='If "get donation consent" is enabled, will be displayed before the debriefing page.', null=True, verbose_name='Donation Briefing Text'),
        ),
        migrations.AddField(
            model_name='pooledproject',
            name='get_donation_consent',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='poolparticipant',
            name='pool_donate',
            field=models.BooleanField(default=None, null=True),
        ),
    ]
