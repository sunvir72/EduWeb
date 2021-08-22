# Generated by Django 2.2.4 on 2020-06-30 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0023_ext_attempt_extqnr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ext_attempt',
            name='mm',
        ),
        migrations.AddField(
            model_name='ext_attempt',
            name='email',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AddField(
            model_name='extqnr',
            name='mm',
            field=models.IntegerField(default=10),
        ),
    ]