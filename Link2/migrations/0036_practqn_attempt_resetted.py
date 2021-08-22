# Generated by Django 2.2.4 on 2021-07-25 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Link2', '0035_studentpractscore'),
    ]

    operations = [
        migrations.CreateModel(
            name='practqn_attempt_resetted',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stat', models.IntegerField()),
                ('email', models.CharField(max_length=200)),
                ('date', models.DateField(auto_now=True)),
                ('time', models.TimeField(auto_now=True)),
                ('time_taken', models.IntegerField()),
                ('ques', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Link2.ques')),
            ],
        ),
    ]