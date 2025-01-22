# Generated by Django 5.1.4 on 2024-12-31 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recrutement', '0002_rename_recrutements_recrutement'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='offre_emploi',
            options={'ordering': ['-date_publication'], 'verbose_name': 'Job Offer', 'verbose_name_plural': 'Job Offers'},
        ),
        migrations.RemoveField(
            model_name='offre_emploi',
            name='body',
        ),
        migrations.AddField(
            model_name='offre_emploi',
            name='date_expiration',
            field=models.DateField(blank=True, null=True, verbose_name='Expiration Date'),
        ),
        migrations.AddField(
            model_name='offre_emploi',
            name='description',
            field=models.TextField(default='No description provided', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='offre_emploi',
            name='date_publication',
            field=models.DateField(verbose_name='Publication Date'),
        ),
        migrations.AlterField(
            model_name='offre_emploi',
            name='statut',
            field=models.CharField(choices=[('Actif', 'Active'), ('Expire', 'Expired'), ('En attente', 'Pending')], default='En attente', max_length=20, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='offre_emploi',
            name='titre',
            field=models.CharField(max_length=300, verbose_name='Title'),
        ),
    ]
