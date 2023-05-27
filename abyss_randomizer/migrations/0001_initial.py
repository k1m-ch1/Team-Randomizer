# Generated by Django 4.2 on 2023-05-27 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CharacterModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ElementType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('icon_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rarity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('star', models.IntegerField()),
                ('icon_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WeaponType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('icon_url', models.URLField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('icon_url', models.URLField(blank=True, null=True)),
                ('element', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='abyss_randomizer.elementtype')),
            ],
        ),
        migrations.CreateModel(
            name='GenshinCharacter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('character_url', models.URLField(blank=True, null=True)),
                ('model_type', models.CharField(blank=True, max_length=64, null=True)),
                ('element', models.ManyToManyField(related_name='characters', to='abyss_randomizer.elementtype')),
                ('quality', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='abyss_randomizer.rarity')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='abyss_randomizer.region')),
                ('weapon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='abyss_randomizer.weapontype')),
            ],
        ),
    ]