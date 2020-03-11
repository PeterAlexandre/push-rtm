# Generated by Django 2.2.5 on 2020-03-11 17:00

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flowhub', '0004_auto_20200311_1141'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flow',
            name='sdgs',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True, choices=[(1, 'No Poverty'), (2, 'Zero Hunger'), (3, 'Good Health and Well-Being'), (4, 'Quality Education'), (5, 'Gender Equality'), (6, 'Clean Water and Sanitation'), (7, 'Affordable And Clean Energy'), (8, 'Decent Work and Economic Growth'), (9, 'Industry, Innovation and Infrastructure'), (10, 'Reduced Inequalities'), (11, 'Sustainable Cities and Communities'), (12, 'Responsible Production and Consumption'), (13, 'Climate Action'), (14, 'Life Below Water'), (15, 'Life On Land'), (16, 'Peace, Justice and Strong Institutions'), (17, 'Partnerships for the Goals')], null=True), size=None, verbose_name='SDGs'),
        ),
    ]
