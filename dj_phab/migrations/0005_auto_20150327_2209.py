# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dj_phab', '0004_lastimporttracker'),
    ]

    operations = [
        migrations.CreateModel(
            name='UpdatedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('filename', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='pullrequest',
            options={'ordering': ['-date_opened']},
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='files',
            field=models.ManyToManyField(related_name='diffs', to='dj_phab.UpdatedFile'),
            preserve_default=True,
        ),
    ]
