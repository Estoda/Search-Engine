# Generated by Django 5.2 on 2025-05-05 03:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search_app', '0009_alter_pagelink_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='outgoing_links',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.DeleteModel(
            name='PageLink',
        ),
    ]
