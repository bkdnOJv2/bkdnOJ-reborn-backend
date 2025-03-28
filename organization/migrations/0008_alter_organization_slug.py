# Generated by Django 4.0.4 on 2022-07-01 16:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0007_alter_organization_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='slug',
            field=models.SlugField(help_text='Organization name shown in URL and also will be used for searching.', max_length=128, unique=True, validators=[django.core.validators.MinLengthValidator(3)], verbose_name='organization slug'),
        ),
    ]
