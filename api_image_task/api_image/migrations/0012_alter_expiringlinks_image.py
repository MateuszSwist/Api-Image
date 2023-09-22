# Generated by Django 4.2.5 on 2023-09-22 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api_image", "0011_alter_uploadedimage_author"),
    ]

    operations = [
        migrations.AlterField(
            model_name="expiringlinks",
            name="image",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="original",
                to="api_image.uploadedimage",
            ),
        ),
    ]
