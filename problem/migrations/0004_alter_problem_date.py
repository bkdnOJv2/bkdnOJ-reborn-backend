# Generated by Django 4.0.4 on 2022-06-17 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problem', '0003_problemtestprofile_custom_checker_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='problem',
            name='date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, help_text='Publish date of problem', null=True),
        ),
    ]
