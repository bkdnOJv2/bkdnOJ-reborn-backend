# Generated by Django 4.0.4 on 2022-06-16 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('problem', '0001_initial'),
        ('judger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='judge',
            name='problems',
            field=models.ManyToManyField(blank=True, related_name='judges', to='problem.problem', verbose_name='problems'),
        ),
        migrations.AddField(
            model_name='judge',
            name='runtimes',
            field=models.ManyToManyField(blank=True, related_name='judges', to='judger.language', verbose_name='judges'),
        ),
    ]
