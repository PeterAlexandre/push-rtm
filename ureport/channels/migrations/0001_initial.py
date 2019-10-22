# Generated by Django 2.2.5 on 2019-10-22 20:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orgs', '0026_fix_org_config_rapidpro'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=255)),
                ('channel_type', models.CharField(max_length=5)),
                ('msg_count', models.PositiveIntegerField()),
                ('ivr_count', models.PositiveIntegerField()),
                ('error_count', models.PositiveIntegerField()),
                ('org', models.ForeignKey(help_text='The organization this channel is part of', on_delete=django.db.models.deletion.PROTECT, related_name='channels', to='orgs.Org', verbose_name='UNCT')),
            ],
        ),
        migrations.CreateModel(
            name='ChannelMonthlyStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('incoming_messages_count', models.PositiveIntegerField()),
                ('outgoing_messages_count', models.PositiveIntegerField()),
                ('incoming_ivr_count', models.PositiveIntegerField()),
                ('outgoing_ivr_count', models.PositiveIntegerField()),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='monthly_stats', to='channels.ChannelStats')),
            ],
        ),
        migrations.CreateModel(
            name='ChannelDailyStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msg_type', models.CharField(max_length=1)),
                ('msg_direction', models.CharField(max_length=1)),
                ('date', models.DateField()),
                ('count', models.PositiveIntegerField()),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_stats', to='channels.ChannelStats')),
            ],
        ),
    ]
