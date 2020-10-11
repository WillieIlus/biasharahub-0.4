# Generated by Django 2.2.12 on 2020-10-11 20:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlacklistIP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=40, unique=True)),
            ],
            options={
                'verbose_name': 'Blacklisted IP',
                'verbose_name_plural': 'Blacklisted IPs',
                'db_table': 'hit_blacklist_ip',
            },
        ),
        migrations.CreateModel(
            name='BlacklistUserAgent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_agent', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Blacklisted User Agent',
                'verbose_name_plural': 'Blacklisted User Agents',
                'db_table': 'hit_blacklist_user_agent',
            },
        ),
        migrations.CreateModel(
            name='Hit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(db_index=True, editable=False, max_length=40)),
                ('session', models.CharField(db_index=True, editable=False, max_length=40)),
                ('user_agent', models.CharField(editable=False, max_length=255)),
                ('hits', models.PositiveIntegerField(default=0)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_type_set_for_hit', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'hit',
                'verbose_name_plural': 'hits',
                'ordering': ('-hits', '-created'),
                'get_latest_by': ('created', 'modified'),
                'unique_together': {('content_type', 'object_id')},
            },
        ),
    ]
