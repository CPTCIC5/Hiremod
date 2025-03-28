# Generated by Django 5.1.5 on 2025-02-02 10:59

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organization', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='JobPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('job_desc', models.TextField()),
                ('workplace_type', models.IntegerField(choices=[(1, 'Hybrid'), (2, 'On-Site'), (3, 'Remote')])),
                ('location', models.CharField(max_length=100)),
                ('job_type', models.IntegerField(choices=[(1, 'Full-time'), (2, 'Part-time'), (3, 'Contract'), (4, 'Temperory'), (5, 'Other'), (6, 'Volunteer'), (7, 'Internship')])),
                ('portal_link', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Candidate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.IntegerField(choices=[(1, 'New Lead'), (2, 'Contacted'), (3, 'Responded'), (4, 'Applied'), (5, 'Recruiter screen'), (6, 'Second interview'), (7, 'Onsite'), (8, 'Offer')])),
                ('resume', models.FileField(upload_to='Candidates-Resume', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])])),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.jobpost')),
            ],
        ),
    ]
