# Generated by Django 2.2.12 on 2020-09-25 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=200, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('publish', models.DateTimeField(auto_now_add=True, verbose_name='date published')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('icon', models.CharField(blank=True, default='', max_length=256, null=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
    ]
