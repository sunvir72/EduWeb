# Generated by Django 3.2.4 on 2021-07-17 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0033_assignments_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignments',
            name='islive',
            field=models.BooleanField(default=True),
        ),
    ]