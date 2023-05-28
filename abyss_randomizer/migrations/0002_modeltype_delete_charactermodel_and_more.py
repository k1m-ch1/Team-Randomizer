# Generated by Django 4.2 on 2023-05-28 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abyss_randomizer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModelType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.DeleteModel(
            name='CharacterModel',
        ),
        migrations.RemoveField(
            model_name='genshincharacter',
            name='model_type',
        ),
        migrations.AddField(
            model_name='genshincharacter',
            name='model_type',
            field=models.ManyToManyField(related_name='characters', to='abyss_randomizer.modeltype'),
        ),
    ]
