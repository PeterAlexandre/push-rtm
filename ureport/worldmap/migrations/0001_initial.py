# Generated by Django 2.2.5 on 2020-01-31 20:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orgs', '0026_fix_org_config_rapidpro'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrgCountryCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_country_code', models.CharField(max_length=2)),
                ('org', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='org_country_code', to='orgs.Org')),
            ],
        ),
    ]
