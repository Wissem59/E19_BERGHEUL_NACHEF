# Generated by Django 5.1.4 on 2024-12-31 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recrutement', '0003_alter_offre_emploi_options_remove_offre_emploi_body_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='offre_emploi',
            name='lieu',
            field=models.CharField(default='Not specified', max_length=255, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='offre_emploi',
            name='type_contrat',
            field=models.CharField(default='Not specified', max_length=100, verbose_name='Contract Type'),
        ),
    ]
