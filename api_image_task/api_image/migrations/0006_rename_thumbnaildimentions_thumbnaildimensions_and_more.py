# Generated by Django 4.2.5 on 2023-09-21 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("api_image", "0005_alter_expiringlinks_image"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="ThumbnailDimentions",
            new_name="ThumbnailDimensions",
        ),
        migrations.RenameModel(
            old_name="ImageModel",
            new_name="UploadedImage",
        ),
        migrations.RenameField(
            model_name="accounttier",
            old_name="image_size",
            new_name="image_sizes",
        ),
        migrations.RenameField(
            model_name="accounttier",
            old_name="orginal_image_link",
            new_name="orginal_image_acces",
        ),
        migrations.RenameField(
            model_name="accounttier",
            old_name="time_limited_link",
            new_name="time_limited_link_acces",
        ),
        migrations.AlterField(
            model_name="imagexaccount",
            name="account_type",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="account_type",
                to="api_image.accounttier",
            ),
        ),
    ]