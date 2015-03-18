# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dj_phab', '0003_auto_20150317_1921'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastImportTracker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_import_time', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
