# Generated by Django 4.0.2 on 2022-03-06 04:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_bid_auctions'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bid',
            options={'ordering': ['-date']},
        ),
        migrations.AlterField(
            model_name='auction_listing',
            name='item_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='auction_category', to='auctions.category'),
        ),
    ]
