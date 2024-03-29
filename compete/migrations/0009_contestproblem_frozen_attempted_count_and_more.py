# Generated by Django 4.0.4 on 2022-08-08 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compete', '0008_contest_standing_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='contestproblem',
            name='frozen_attempted_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of users who has attempted this problem before frozen time'),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='frozen_solved_count',
            field=models.PositiveIntegerField(default=0, help_text='Number of users who has solved this problem before frozen time'),
        ),
        migrations.AddField(
            model_name='contestproblem',
            name='modified',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='modified date'),
        ),
    ]
