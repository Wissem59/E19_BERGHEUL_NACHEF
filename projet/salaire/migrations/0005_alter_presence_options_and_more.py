# Generated by Django 5.1.4 on 2025-01-15 23:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_personnel_date_naissance'),
        ('salaire', '0004_alter_presence_id_employe'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='presence',
            options={'verbose_name': 'Presence', 'verbose_name_plural': 'Presences'},
        ),
        migrations.RemoveField(
            model_name='salaire',
            name='massrouf_annuel',
        ),
        migrations.RemoveField(
            model_name='salaire',
            name='massrouf_fois',
        ),
        migrations.AlterField(
            model_name='salaire',
            name='massrouf_mensuel',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salaire',
            name='prime_festive',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salaire',
            name='prime_performance',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salaire',
            name='prime_total',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salaire',
            name='salaire_base',
            field=models.DecimalField(decimal_places=2, default=30000.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='salaire',
            name='salaire_jour',
            field=models.DecimalField(decimal_places=2, default=2000.0, max_digits=10),
        ),
        migrations.CreateModel(
            name='Massrouf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('massrouf_fois', models.IntegerField()),
                ('montant', models.FloatField()),
                ('annee', models.IntegerField()),
                ('id_employe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.personnel')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('annee', 'id_employe'), name='unique_annee_employe')],
            },
        ),
    ]
