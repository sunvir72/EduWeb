# Generated by Django 2.2.4 on 2020-04-23 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0013_auto_20200421_0232'),
    ]

    operations = [
        migrations.AddField(
            model_name='resaccess',
            name='topic',
            field=models.CharField(default='none', max_length=200),
        ),
    ]
