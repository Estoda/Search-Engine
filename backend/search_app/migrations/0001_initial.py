# Generated by Django 4.2.14 on 2025-05-03 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('title', models.CharField(blank=True, max_length=300)),
                ('content', models.TextField()),
                ('rank', models.FloatField(default=0.0)),
            ],
        ),
    ]
