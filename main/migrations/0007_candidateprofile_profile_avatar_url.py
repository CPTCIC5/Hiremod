# Generated by Django 5.1.5 on 2025-02-20 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_alter_channel_channel_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidateprofile',
            name='profile_avatar_url',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
