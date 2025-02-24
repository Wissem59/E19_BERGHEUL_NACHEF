# Generated by Django 5.1.4 on 2025-01-03 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recrutement', '0006_alter_candidature_statut_candidature'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidature',
            name='telephone_candidat',
            field=models.IntegerField(blank=True, null=True, verbose_name='Candidate Telephone'),
        ),
        migrations.AlterField(
            model_name='candidature',
            name='email_candidat',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Candidate Email'),
        ),
    ]
