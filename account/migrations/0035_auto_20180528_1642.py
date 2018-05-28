# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-05-28 16:42
from __future__ import unicode_literals

from django.db import migrations


def update_users(apps, schema_editor):
    UserModel = apps.get_model('account', 'User')

    for user in UserModel.objects.all():
        user.accepted_privacy_policy_date = user.date_joined
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0034_auto_20180528_1642'),
    ]

    operations = [
        migrations.RunPython(update_users),
    ]