# Generated by Django 2.2.4 on 2020-04-20 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0012_auto_20200419_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignments',
            name='topic',
            field=models.CharField(default='None', max_length=200),
        ),
        migrations.AddField(
            model_name='links',
            name='topic',
            field=models.CharField(default='None', max_length=200),
        ),
    ]
