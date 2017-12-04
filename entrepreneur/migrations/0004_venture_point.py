# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-10-09 15:49
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entrepreneur', '0003_auto_20171004_0459'),
    ]

    operations = [
        migrations.AddField(
            model_name='venture',
            name='point',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326, verbose_name='posición'),
        ),
    ]
