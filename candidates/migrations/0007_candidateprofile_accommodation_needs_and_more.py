# Generated by Django 5.1.5 on 2025-04-09 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0006_remove_candidateprompt_convo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='accommodation_needs',
            field=models.CharField(choices=[('YES', 'YES'), ('NO', 'NO'), ('PREFER TO DISCUSS LATER', 'PREFER TO DISCUSS LATER')], default=[], max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='disability_categories',
            field=models.JSONField(default=list, help_text='Array for Disability criterias"s '),
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='workplace_accommodations',
            field=models.JSONField(default=list, help_text='Accommodations for WorkPlace'),
        ),
    ]
