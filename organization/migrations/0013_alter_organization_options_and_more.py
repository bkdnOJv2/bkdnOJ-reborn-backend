# Generated by Django 4.0.4 on 2022-08-05 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0012_organization_is_protected'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organization',
            options={'ordering': ['name'], 'permissions': (('create_root_organization', 'Create root Organization'), ('move_organization_anywhere', 'Move organization to others parents or let it become root itself.'), ('see_all_organizations', 'Can see all organizations, including private ones.'), ('join_private_organization', 'Join private (is_open=False) organization.'), ('join_without_access_code', 'Join protected organization without access code.')), 'verbose_name': 'organization', 'verbose_name_plural': 'organizations'},
        ),
        migrations.AlterField(
            model_name='organization',
            name='access_code',
            field=models.CharField(blank=True, help_text='Student access code', max_length=16, null=True, verbose_name='access code'),
        ),
    ]
