# Generated by Django 4.2.5 on 2023-09-21 16:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("api_image", "0009_alter_uploadedimage_upload_image"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expiringlinks",
            name="owner",
        ),
        migrations.AlterField(
            model_name="uploadedimage",
            name="upload_image",
            field=models.ImageField(upload_to=""),
        ),
    ]