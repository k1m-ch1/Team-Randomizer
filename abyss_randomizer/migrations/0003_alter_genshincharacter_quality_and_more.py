# Generated by Django 4.2 on 2023-05-28 06:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('abyss_randomizer', '0002_modeltype_delete_charactermodel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genshincharacter',
            name='quality',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='abyss_randomizer.rarity'),
        ),
        migrations.AlterField(
            model_name='genshincharacter',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='characters', to='abyss_randomizer.region'),
        ),
    ]
