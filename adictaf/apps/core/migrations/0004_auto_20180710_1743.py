# Generated by Django 2.0.4 on 2018-07-10 17:43

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_advert'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='device_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='project',
            name='force_login',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='last_json',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_session_time',
            field=models.PositiveIntegerField(default=1000000),
        ),
        migrations.AddField(
            model_name='project',
            name='proxy',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AddField(
            model_name='project',
            name='user_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='uuid',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
