# Generated by Django 2.2.4 on 2020-06-26 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0019_auto_20200625_1923'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ques',
            name='qnr',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Link2.questr'),
        ),
    ]
