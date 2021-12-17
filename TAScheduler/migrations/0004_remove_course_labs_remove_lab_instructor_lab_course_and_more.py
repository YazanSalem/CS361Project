# Generated by Django 4.0 on 2021-12-16 23:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('TAScheduler', '0003_rename_useraddress_userprofile_address_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='labs',
        ),
        migrations.RemoveField(
            model_name='lab',
            name='instructor',
        ),
        migrations.AddField(
            model_name='lab',
            name='course',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='TAScheduler.course'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='course',
            name='hours',
            field=models.CharField(max_length=20),
        ),
    ]
