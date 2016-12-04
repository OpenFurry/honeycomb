# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-04 01:29
from __future__ import unicode_literals

from django.db import migrations, models
import publishers.models


class Migration(migrations.Migration):

    dependencies = [
        ('publishers', '0004_auto_20161204_0116'),
    ]

    operations = [
        migrations.AddField(
            model_name='publisherpage',
            name='banner',
            field=models.ImageField(blank=True, upload_to=publishers.models.banner_path),
        ),
        migrations.AddField(
            model_name='publisherpage',
            name='logo',
            field=models.ImageField(default=' ', upload_to=publishers.models.logo_path),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='newsitem',
            name='image',
            field=models.ImageField(blank=True, upload_to=publishers.models.newsitem_path),
        ),
    ]
