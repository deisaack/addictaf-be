# Generated by Django 2.0.4 on 2018-05-24 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20180524_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video_sm',
            field=models.FileField(blank=True, null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='post',
            name='caption',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
