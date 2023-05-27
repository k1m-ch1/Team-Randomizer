from django.shortcuts import render
from django.http import JsonResponse

import requests
from .models import *
from . import scrape_data_from_web as scraper
import re


GENSHIN_CHARACTER_URL = 'https://genshin-impact.fandom.com/wiki/Character'

def add_or_update_database():
  pass

# Create your views here.

def get_object(django_table, **kwargs):
  result = django_table.objects.filter(**kwargs)
  if len(result) == 0:
    return None
  else:
    return result.first()

def filter_object(django_table, **kwargs):
  result = django_table.objects.filter(**kwargs)
  if len(result) == 0:
    return None
  else:
    return result

def index(request):
  weapons = scraper.get_formatted_table('weapons')
  regions = scraper.get_formatted_table('regions')
  characters = scraper.get_formatted_table('characters')
  
  
  for weapon in weapons:
    if len(WeaponType.objects.filter(name=weapon['Type']['text'][:-1])) == 0:
      WeaponType(name=weapon['Type']['text'][:-1], icon_url=weapon['Icon']['img_src']).save()
      print(f"Created new object called {weapon['Type']['text']}")
  
  for element in regions:
    if len(ElementType.objects.filter(name=element['Element']['text'])) == 0:
      ElementType(name=element['Element']['text'], icon_url=element['Element']['img_src']).save()
      print(f"Created new object called {element['Element']['text']}")
      
  
  for rarity in characters:
    if len(Rarity.objects.filter(star = int(re.search(r'.+Icon_([0-9])_Stars.png.+', rarity['Quality']['img_src']).group(1)))) == 0:
      Rarity(icon_url=rarity['Quality']['img_src'], star=int(re.search(r'.+Icon_([0-9])_Stars.png.+', rarity['Quality']['img_src']).group(1))).save()
      print(f"Created new object called {rarity['Quality']['img_src']}")

  
  for region in regions:
    if len(Region.objects.filter(name=region['Nation']['text'])) == 0:
      Region(name=region['Nation']['text'], icon_url=region['Nation']['img_src'], element=ElementType.objects.get(name=region['Element']['text'])).save()
      print(f"Created new object called {region['Nation']['text']}")

  for character in characters:
    if len(GenshinCharacter.objects.filter(name=character['Name']['text'])) == 0:
      new_character = GenshinCharacter.objects.create(name=character['Name']['text'],
                       character_url=character['Icon']['img_src'],
                       weapon=WeaponType.objects.get(name=character['Weapon']['text']),
                       quality=Rarity.objects.get(star=int(re.search(r'.+Icon_([0-9])_Stars.png.+', character['Quality']['img_src']).group(1))),
                       region=get_object(Region, name=character['Region']['text']),
                       model_type=character['Model Type']['text'])
      try:
        for element in filter_object(ElementType, name=character['Element']['text']):
          new_character.element.add(element)
        
        new_character.save()
      except:
        pass
      

      print(f"Created new object called {character['Name']['text']}")
      
  
  return render(request, 'abyss_randomizer/index.html', {
    'characters': scraper.get_element_from_column('characters', 'Weapon', 'text')
  })

def get_table_info(request, table_name):
  return JsonResponse(scraper.get_formatted_table(table_name), safe=False)