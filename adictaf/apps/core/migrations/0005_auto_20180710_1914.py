# Generated by Django 2.0.4 on 2018-07-10 19:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20180710_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='user_id',
            field=models.BigIntegerField(default=0),
        ),
    ]
