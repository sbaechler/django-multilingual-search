# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testproject', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParlerDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('docid', models.CharField(max_length=100)),
                ('genre', models.CharField(max_length=20)),
                ('origlang', models.CharField(max_length=10)),
            ],
            options={
                'ordering': ['docid'],
                'verbose_name': 'Parler Document',
            },
        ),
        migrations.CreateModel(
            name='ParlerDocumentTranslation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('language_code', models.CharField(db_index=True, max_length=15, verbose_name='Language')),
                ('text', models.TextField()),
                ('title', models.TextField(blank=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, null=True, to='testproject.ParlerDocument')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Parler Document Translation',
                'db_tablespace': '',
                'db_table': 'testproject_parlerdocument_translation',
                'managed': True,
            },
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'ordering': ['docid'], 'verbose_name': 'Modeltranslations Document'},
        ),
        migrations.AlterUniqueTogether(
            name='parlerdocumenttranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
