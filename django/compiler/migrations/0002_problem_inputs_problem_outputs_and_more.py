# Generated by Django 5.1 on 2024-09-09 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compiler', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='inputs',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='problem',
            name='outputs',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='submission',
            name='verdict',
            field=models.CharField(default='Failed', max_length=30),
        ),
    ]
