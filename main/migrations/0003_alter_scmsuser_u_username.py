# Generated by Django 5.0.2 on 2024-03-03 14:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_alter_scmsuser_u_password"),
    ]

    operations = [
        migrations.AlterField(
            model_name="scmsuser",
            name="u_username",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
