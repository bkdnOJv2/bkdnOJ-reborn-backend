# Generated by Django 4.0.4 on 2022-06-24 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0004_rename_creation_date_organization_created'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organization',
            old_name='created',
            new_name='creation_date',
        ),
    ]
