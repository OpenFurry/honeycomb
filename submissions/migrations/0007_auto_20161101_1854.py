# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-01 18:54
from __future__ import unicode_literals

from django.db import migrations, models
import submissions.models


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0006_auto_20161031_0625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='content_file',
            field=models.FileField(blank=True, upload_to=submissions.models.content_path),
        ),
        migrations.AlterField(
            model_name='submission',
            name='cover',
            field=models.ImageField(blank=True, upload_to=submissions.models.cover_path),
        ),
        migrations.AlterField(
            model_name='submission',
            name='icon',
            field=models.ImageField(blank=True, upload_to=submissions.models.icon_path),
        ),
    ]