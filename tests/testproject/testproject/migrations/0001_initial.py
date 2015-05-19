# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('docid', models.CharField(max_length=100)),
                ('genre', models.CharField(max_length=20)),
                ('origlang', models.CharField(max_length=10)),
                ('text', models.TextField()),
                ('text_en', models.TextField(null=True)),
                ('text_de', models.TextField(null=True)),
                ('text_es', models.TextField(null=True)),
                ('text_fr', models.TextField(null=True)),
                ('text_cs', models.TextField(null=True)),
                ('text_ru', models.TextField(null=True)),
                ('title', models.TextField(blank=True)),
                ('title_en', models.TextField(blank=True, null=True)),
                ('title_de', models.TextField(blank=True, null=True)),
                ('title_es', models.TextField(blank=True, null=True)),
                ('title_fr', models.TextField(blank=True, null=True)),
                ('title_cs', models.TextField(blank=True, null=True)),
                ('title_ru', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ['docid'],
                'verbose_name': 'Document',
            },
        ),
    ]
