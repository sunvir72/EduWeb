# Generated by Django 2.2.4 on 2020-06-26 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0020_auto_20200626_1230'),
    ]

    operations = [
        migrations.AddField(
            model_name='practqn_attempt',
            name='date',
            field=models.DateField(auto_now=True),
        ),
    ]