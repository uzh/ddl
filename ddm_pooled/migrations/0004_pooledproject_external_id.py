# Generated by Django 3.2.13 on 2023-06-18 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ddm_pooled', '0003_poolparticipant_external_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='pooledproject',
            name='external_id',
            field=models.CharField(default='a', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]