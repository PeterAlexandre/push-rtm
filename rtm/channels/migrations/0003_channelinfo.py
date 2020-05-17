# Generated by Django 2.2.5 on 2020-05-17 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("channels", "0002_channelmonthlystats_error_count"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChannelInfo",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("urn", models.CharField(max_length=5, unique=True)),
                ("name", models.CharField(blank=True, max_length=100, null=True)),
                ("icon", models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
