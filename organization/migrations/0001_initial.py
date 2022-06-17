# Generated by Django 4.0.4 on 2022-06-16 09:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='organization title')),
                ('slug', models.SlugField(help_text='Organization name shown in URL', max_length=128, verbose_name='organization slug')),
                ('short_name', models.CharField(help_text='Displayed beside user name during contests', max_length=20, verbose_name='short name')),
                ('about', models.TextField(verbose_name='organization description')),
                ('creation_date', models.DateTimeField(auto_now_add=True, verbose_name='creation date')),
                ('is_open', models.BooleanField(default=True, help_text='Allow joining organization', verbose_name='is open organization?')),
                ('slots', models.IntegerField(blank=True, help_text='Maximum amount of users in this organization, only applicable to private organizations', null=True, verbose_name='maximum size')),
                ('access_code', models.CharField(blank=True, help_text='Student access code', max_length=7, null=True, verbose_name='access code')),
            ],
            options={
                'verbose_name': 'organization',
                'verbose_name_plural': 'organizations',
                'ordering': ['name'],
                'permissions': (('organization_admin', 'Administer organizations'), ('edit_all_organization', 'Edit all organizations')),
            },
        ),
        migrations.CreateModel(
            name='OrganizationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='request time')),
                ('state', models.CharField(choices=[('P', 'Pending'), ('A', 'Approved'), ('R', 'Rejected')], max_length=1, verbose_name='state')),
                ('reason', models.TextField(verbose_name='reason')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='requests', to='organization.organization', verbose_name='organization')),
            ],
            options={
                'verbose_name': 'organization join request',
                'verbose_name_plural': 'organization join requests',
            },
        ),
    ]
