# Generated by Django 5.1.5 on 2025-03-19 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0006_alter_organization_industry'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='assistant_id',
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
