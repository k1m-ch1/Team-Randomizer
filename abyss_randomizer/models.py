from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.



class ModelType(models.Model):
  name = models.CharField(null=False, blank=False, max_length=64)
  
  def __str__(self):
    return f'{self.name}'


class WeaponType(models.Model):
  name = models.CharField(null=False, blank=False, max_length=64)
  icon_url = models.URLField(blank=True, null=True)
  def __str__(self):
    return f"Weapon name: {self.name}"


class ElementType(models.Model):
  name = models.CharField(null=False, blank=False, max_length=64)
  icon_url = models.URLField(blank=True, null=True)
  
  def __str__(self):
    return f"Element name: {self.name}"
  
  
class Rarity(models.Model):
  star = models.IntegerField(null=False, blank=False)
  icon_url = models.URLField(blank=True, null=True)

  def __str__(self):
    return f"Rarity: {self.star}\nLink to url: {self.icon_url}"


class Region(models.Model):
  name = models.CharField(null=False, blank=False, max_length=64)
  icon_url = models.URLField(blank=True, null=True)
  element = models.ForeignKey(ElementType, on_delete=models.CASCADE)
  
  def __str__(self):
    return f'Region: {self.name}'
  
  
class GenshinCharacter(models.Model):
  name = models.CharField(null=False, blank=False, max_length=64)
  character_url = models.URLField(blank=True, null=True)
  weapon = models.ForeignKey(WeaponType, on_delete=models.CASCADE, related_name="characters")
  quality = models.ForeignKey(Rarity, on_delete=models.CASCADE, related_name="characters")
  region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, related_name="characters")
  weapon = models.ForeignKey(WeaponType, on_delete=models.CASCADE, null=False, blank=False)
  element = models.ManyToManyField(ElementType, related_name="characters")
  model_type = models.ManyToManyField(ModelType, related_name="characters")
  
  def __str__(self):
    return f"Character: {self.name}"

class User(AbstractUser):
  uid = models.IntegerField(null=True, blank=True)
  ltuid = models.IntegerField(null=True, blank=True)
  ltoken = models.CharField(null=True, blank=True, max_length=128)
  characters = models.ManyToManyField(GenshinCharacter)
  