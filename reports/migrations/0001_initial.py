# Generated by Django 3.2.17 on 2024-08-30 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramStatistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('follow_counts', models.JSONField(default=None, null=True)),
                ('biodiversity_counts', models.JSONField(default=None, null=True)),
                ('pension_counts', models.JSONField(default=None, null=True)),
                ('party_counts', models.JSONField(default=None, null=True)),
                ('social_media_use', models.JSONField()),
                ('last_updated', models.DateTimeField(blank=True, null=True)),
                ('project_pk', models.IntegerField(default=0)),
            ],
        ),
    ]
