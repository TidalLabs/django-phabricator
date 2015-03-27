# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dj_phab', '0005_auto_20150327_2209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='updatedfile',
            name='filename',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
    ]
