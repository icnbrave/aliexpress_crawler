# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-30 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aliexpress', '0008_queryresult_overall_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='pages',
            field=models.IntegerField(blank=True, default=1, null=True, verbose_name='查询页数'),
        ),
    ]
