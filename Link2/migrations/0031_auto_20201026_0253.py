# Generated by Django 2.2.4 on 2020-10-25 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0030_auto_20201025_2146'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questr',
            name='time_taken',
        ),
        migrations.AddField(
            model_name='qnr_attempt',
            name='time_taken',
            field=models.IntegerField(default=3600),
            preserve_default=False,
        ),
    ]