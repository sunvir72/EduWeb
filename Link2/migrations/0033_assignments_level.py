# Generated by Django 3.2.4 on 2021-07-17 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0032_auto_20210620_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignments',
            name='level',
            field=models.IntegerField(default=1),
        ),
    ]