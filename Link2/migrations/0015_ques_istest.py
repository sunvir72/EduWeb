# Generated by Django 2.2.4 on 2020-05-07 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0014_resaccess_topic'),
    ]

    operations = [
        migrations.AddField(
            model_name='ques',
            name='istest',
            field=models.IntegerField(default=0),
        ),
    ]
