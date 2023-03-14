# Generated by Django 4.1.7 on 2023-03-14 00:24

from django.db import migrations, models
import django.db.models.deletion
import store.models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_alter_reviewrating_product'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductGallery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(max_length=255, upload_to=store.models.ProductGallery.image_upload_to)),
                ('product', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
    ]
