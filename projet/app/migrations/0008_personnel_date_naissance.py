# Generated by Django 5.1.4 on 2025-01-14 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_remove_conge_jours_restants_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='personnel',
            name='date_naissance',
            field=models.DateField(default='1990-01-01'),
        ),
    ]
