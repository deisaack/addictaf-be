# Generated by Django 2.0.4 on 2018-05-23 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20180523_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='caption',
            field=models.TextField(blank=True, null=True),
        ),
    ]
