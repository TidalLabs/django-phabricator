# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dj_phab', '0002_auto_20150313_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pullrequest',
            name='repository',
            field=models.ForeignKey(blank=True, to='dj_phab.Repository', null=True),
            preserve_default=True,
        ),
    ]
