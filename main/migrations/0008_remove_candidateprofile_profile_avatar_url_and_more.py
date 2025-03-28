# Generated by Django 5.1.5 on 2025-02-20 10:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_candidateprofile_profile_avatar_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='candidateprofile',
            name='profile_avatar_url',
        ),
        migrations.AddField(
            model_name='candidateprofile',
            name='profile_avatar',
            field=models.ImageField(default='xgz.jpg', upload_to='Candidate-Photo', validators=[django.core.validators.validate_image_file_extension]),
            preserve_default=False,
        ),
    ]
