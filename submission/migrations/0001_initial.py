# Generated by Django 4.0.4 on 2022-06-16 09:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('compete', '0001_initial'),
        ('problem', '0001_initial'),
        ('judger', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='submission time')),
                ('time', models.FloatField(db_index=True, null=True, verbose_name='execution time')),
                ('memory', models.FloatField(null=True, verbose_name='memory usage')),
                ('points', models.FloatField(db_index=True, null=True, verbose_name='points granted')),
                ('status', models.CharField(choices=[('QU', 'Queued'), ('P', 'Processing'), ('G', 'Grading'), ('D', 'Completed'), ('IE', 'Internal Error'), ('CE', 'Compile Error'), ('AB', 'Aborted')], db_index=True, default='QU', max_length=2, verbose_name='status')),
                ('result', models.CharField(blank=True, choices=[('AC', 'Accepted'), ('WA', 'Wrong Answer'), ('TLE', 'Time Limit Exceeded'), ('MLE', 'Memory Limit Exceeded'), ('OLE', 'Output Limit Exceeded'), ('IR', 'Invalid Return'), ('RTE', 'Runtime Error'), ('CE', 'Compile Error'), ('IE', 'Internal Error'), ('SC', 'Short circuit'), ('AB', 'Aborted')], db_index=True, default=None, max_length=3, null=True, verbose_name='result')),
                ('error', models.TextField(blank=True, null=True, verbose_name='compile errors')),
                ('current_testcase', models.IntegerField(default=0)),
                ('batch', models.BooleanField(default=False, verbose_name='batched cases')),
                ('case_points', models.FloatField(default=0, verbose_name='test case points')),
                ('case_total', models.FloatField(default=0, verbose_name='test case total points')),
                ('judged_date', models.DateTimeField(default=None, null=True, verbose_name='submission judge time')),
                ('rejudged_date', models.DateTimeField(blank=True, null=True, verbose_name='last rejudge date by admin')),
                ('is_pretested', models.BooleanField(default=False, verbose_name='was ran on pretests only')),
                ('locked_after', models.DateTimeField(blank=True, null=True, verbose_name='submission lock')),
                ('contest_object', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='compete.contest', verbose_name='contest')),
                ('judged_on', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='judger.judge', verbose_name='judged on')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judger.language', verbose_name='submission language')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problem.problem', verbose_name='problem')),
            ],
            options={
                'verbose_name': 'submission',
                'verbose_name_plural': 'submissions',
                'ordering': ['-id'],
                'permissions': (('abort_any_submission', 'Abort any submission'), ('rejudge_submission', 'Rejudge the submission'), ('rejudge_submission_lot', 'Rejudge a lot of submissions'), ('spam_submission', 'Submit without limit'), ('view_all_submission', 'View all submission'), ('resubmit_other', "Resubmit others' submission"), ('lock_submission', 'Change lock status of submission')),
            },
        ),
        migrations.CreateModel(
            name='SubmissionTestCase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('case', models.IntegerField(verbose_name='test case ID')),
                ('status', models.CharField(choices=[('AC', 'Accepted'), ('WA', 'Wrong Answer'), ('TLE', 'Time Limit Exceeded'), ('MLE', 'Memory Limit Exceeded'), ('OLE', 'Output Limit Exceeded'), ('IR', 'Invalid Return'), ('RTE', 'Runtime Error'), ('CE', 'Compile Error'), ('IE', 'Internal Error'), ('SC', 'Short circuit'), ('AB', 'Aborted')], max_length=3, verbose_name='status flag')),
                ('time', models.FloatField(null=True, verbose_name='execution time')),
                ('memory', models.FloatField(null=True, verbose_name='memory usage')),
                ('points', models.FloatField(null=True, verbose_name='points granted')),
                ('total', models.FloatField(null=True, verbose_name='points possible')),
                ('batch', models.IntegerField(null=True, verbose_name='batch number')),
                ('feedback', models.CharField(blank=True, max_length=50, verbose_name='judging feedback')),
                ('extended_feedback', models.TextField(blank=True, verbose_name='extended judging feedback')),
                ('output', models.TextField(blank=True, verbose_name='program output')),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_cases', to='submission.submission', verbose_name='associated submission')),
            ],
            options={
                'verbose_name': 'submission test case',
                'verbose_name_plural': 'submission test cases',
            },
        ),
        migrations.CreateModel(
            name='SubmissionSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.TextField(max_length=65536, verbose_name='source code')),
                ('submission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='source', to='submission.submission', verbose_name='associated submission')),
            ],
            options={
                'verbose_name': 'submission source',
                'verbose_name_plural': 'submission sources',
            },
        ),
    ]
