# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-26 14:31
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=24, null=True, verbose_name='国家名称')),
                ('lang_code', models.CharField(max_length=8, unique=True, verbose_name='语言代码')),
                ('url', models.CharField(max_length=128, unique=True, verbose_name='站点链接')),
            ],
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keywords', models.CharField(max_length=64, verbose_name='查询关键字')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='查询时间')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aliexpress.Country', verbose_name='查询站点')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='查询用户')),
            ],
        ),
        migrations.CreateModel(
            name='QueryResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=64, null=True, verbose_name='商品名称')),
                ('price', models.CharField(blank=True, max_length=64, null=True, verbose_name='商品价格')),
                ('order', models.CharField(blank=True, max_length=64, null=True, verbose_name='订单量')),
                ('store', models.CharField(blank=True, max_length=64, null=True, verbose_name='店铺名称')),
                ('rank', models.IntegerField(blank=True, default=0, null=True, verbose_name='同类商品排名')),
                ('page_number', models.IntegerField(blank=True, default=0, null=True, verbose_name='所在页数')),
                ('query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aliexpress.Query', verbose_name='查询关键字')),
            ],
        ),
    ]
