# Generated by Django 5.1.5 on 2025-04-04 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_jobpost_estimated_salary_delete_candidateprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobpost',
            name='matched_candidates',
            field=models.JSONField(blank=True, default=list, help_text='List of matched candidate slugs with scores'),
        ),
    ]
