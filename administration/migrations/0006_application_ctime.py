# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-07 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0005_auto_20161107_0412'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='ctime',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
