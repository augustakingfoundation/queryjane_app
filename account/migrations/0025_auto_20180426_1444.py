# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-04-26 14:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_usermessage_conversation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
    ]
