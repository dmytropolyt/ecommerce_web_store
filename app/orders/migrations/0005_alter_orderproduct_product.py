# Generated by Django 4.1.7 on 2023-03-17 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_productgallery_options_and_more'),
        ('orders', '0004_alter_orderproduct_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_product', to='store.product'),
        ),
    ]
