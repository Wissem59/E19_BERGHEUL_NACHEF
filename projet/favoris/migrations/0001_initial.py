# Generated by Django 5.1.4 on 2025-01-18 18:04

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Favorite_section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_on', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_sections', to=settings.AUTH_USER_MODEL)),
                ('section_url', models.ForeignKey(db_column='section_url', on_delete=django.db.models.deletion.CASCADE, related_name='favorite_sections', to='favoris.section')),
            ],
            options={
                'unique_together': {('user', 'section_url')},
            },
        ),
    ]
