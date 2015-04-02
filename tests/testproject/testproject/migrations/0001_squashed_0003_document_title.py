# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    replaces = [('testproject', '0001_initial'), ('testproject', '0002_document_language'), ('testproject', '0003_document_title')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('docid', models.CharField(max_length=100)),
                ('genre', models.CharField(max_length=20)),
                ('origlang', models.CharField(max_length=10)),
                ('text', models.TextField()),
                ('language', models.CharField(default='en', max_length=10)),
                ('title', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['docid'],
                'verbose_name': 'Document',
            },
        ),
    ]
