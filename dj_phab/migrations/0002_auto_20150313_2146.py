# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dj_phab', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phabuser',
            name='user_name',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
    ]
