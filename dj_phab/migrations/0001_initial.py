# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PhabUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('phid', models.CharField(unique=True, max_length=30)),
                ('user_name', models.CharField(max_length=255)),
                ('real_name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['real_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('phid', models.CharField(unique=True, max_length=30)),
                ('phab_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('phid', models.CharField(unique=True, max_length=30)),
                ('phab_id', models.IntegerField()),
                ('title', models.CharField(max_length=255)),
                ('line_count', models.PositiveIntegerField()),
                ('status', models.SmallIntegerField(choices=[(0, 'Needs Review'), (1, 'Needs Revision'), (2, 'Accepted'), (3, 'Closed'), (4, 'Abandoned'), (5, 'Changes Planned'), (0, 'In Preparation')])),
                ('uri', models.URLField()),
                ('diff_count', models.PositiveSmallIntegerField()),
                ('commit_count', models.PositiveSmallIntegerField()),
                ('date_opened', models.DateTimeField()),
                ('date_updated', models.DateTimeField()),
                ('author', models.ForeignKey(to='dj_phab.PhabUser')),
            ],
            options={
                'ordering': ['date_opened'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('phid', models.CharField(unique=True, max_length=30)),
                ('phab_id', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
                ('callsign', models.CharField(help_text='Abbreviated, unique name', max_length=16)),
                ('monogram', models.CharField(help_text='Version of callsign used for references in markup', max_length=16)),
                ('uri', models.URLField(help_text='URL to access on Phabricator')),
                ('remote_uri', models.CharField(help_text='URI of origin repo', max_length=255)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['callsign'],
                'verbose_name_plural': 'Repositories',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='repository',
            field=models.ForeignKey(to='dj_phab.Repository'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='reviewers',
            field=models.ManyToManyField(related_name='reviews', to='dj_phab.PhabUser'),
            preserve_default=True,
        ),
    ]
