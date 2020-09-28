# Generated by Django 2.2.12 on 2020-09-28 19:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('business', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpeningHours',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weekday', models.IntegerField(choices=[(1, 'Monday'), (2, 'Tuesday'), (3, 'Wednesday'), (4, 'Thursday'), (5, 'Friday'), (6, 'Saturday'), (7, 'Sunday')], verbose_name='Weekday')),
                ('start', models.TimeField(default='8:00', verbose_name='Start')),
                ('end', models.TimeField(default='18:00', verbose_name='End')),
                ('closed', models.BooleanField(verbose_name='Closed')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opening_hours', to='business.Business', verbose_name='company')),
            ],
            options={
                'verbose_name': 'Opening Hours',
                'verbose_name_plural': 'Opening Hours',
                'ordering': ['company', 'weekday', 'start'],
            },
        ),
    ]
