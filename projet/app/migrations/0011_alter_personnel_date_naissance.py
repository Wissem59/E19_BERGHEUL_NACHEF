# Generated by Django 5.1.4 on 2025-01-19 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_alter_personnel_phone_alter_personnel_date_naissance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personnel',
            name='date_naissance',
            field=models.DateField(),
        ),
    ]
