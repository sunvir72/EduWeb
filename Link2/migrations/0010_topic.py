# Generated by Django 2.2.4 on 2020-04-16 20:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0009_auto_20200327_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Link2.List')),
            ],
        ),
    ]
