from django.shortcuts import render
from django.http import JsonResponse

import requests
from .models import *
from . import scrape_data_from_web as scraper
import re
from functools import reduce
from operator import add


GENSHIN_CHARACTER_URL = 'https://genshin-impact.fandom.com/wiki/Character'
HEIGHT = ['Tall', 'Medium', 'Short']
GENDER = ['Male', 'Female']
MODEL_TYPE = reduce(add, (lambda x, y: list(map(lambda i: list(map(lambda j: i + ' ' + j, y)), x)))(HEIGHT, GENDER))


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
  


def add_update_or_pass_to_database(table_name, table_class, base_keys, update_keys, many_to_many_keys=None):
  """
    table_name is the name of the table like 'characters', 'regions', ...
    table_class is the Model name of the table like Region, GenshinCharacters
    update_keys is a dictionary that will be passed as arguments where the key is a name of the column of the Model table. The value will be a higher order function that will have a formatted_hr passed in
    base_keys are the keys from update_keys that should be checked to prevent duplicates. For example if there's already a row for 'Traveler' but the new data has a different Element columns, we don't want another 'Traveler' row but instead we want to update the existing 'Traveler' row
  """
  
  list_of_hr_formatted= scraper.get_formatted_table(table_name)
  
  for hr_formatted in list_of_hr_formatted:
    new_row_non_rel = { k: v(hr_formatted) for k, v in update_keys.items()}
    # v(hr_formatted) will be a list that contains the many to many elements
    
    if many_to_many_keys is not None:
      
      new_row_rel = { k: v(hr_formatted) for k, v in many_to_many_keys.items()}
    else:
      new_row_rel = None
    
    old_row = table_class.objects.filter(**{ k: v for k, v in new_row_non_rel.items() if k in base_keys})
    
    def compare_many_to_many():
      
      table_class.objects.filter(**new_row_rel)
      
    
    
    if len(table_class.objects.filter(**new_row_non_rel)) == 0 and many_to_many_keys:
      # If doesn't exists or some field got changed
      
      if len(old_row) > 0:
        # Check whether there's already a row that contains an identifier value. Indentifier value example: name of character, name of element, ...
        old_row.update(**new_row_non_rel)
        print(f'Updated a {table_class} table at {old_row}')
      else:
        # Else create a new table
        table_class(**new_row_non_rel).save()
        print(f'Created a new {table_class} called {old_row}')
        
  


def index(request):
  weapons = scraper.get_formatted_table('weapons')
  regions = scraper.get_formatted_table('regions')
  characters = scraper.get_formatted_table('characters')
  
  for model_type in MODEL_TYPE:
    if len(ModelType.objects.filter(name=model_type)) == 0:
      ModelType(name=model_type).save()
      print(f"Created new object called {model_type}") 
  
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
                       region=get_object(Region, name=character['Region']['text']))
      try:
        result_element = character['Element']['text']
        print(result_element)
        if type(result_element) == list:
          for element in result_element:
            new_character.element.add(get_object(ElementType, name=element))
        else:
            new_character.element.add(get_object(ElementType, name=result_element))
        
        result_model = character['Model Type']['text']
        print(result_model)
        if type(result_element) == list:
          for model in result_model:
            new_character.model_type.add(get_object(ModelType, name=model))
          else:
            new_character.model_type.add(get_object(ModelType, name=result_model))
        
        new_character.save()
      except:
        pass
      
      print(f"Created new object called {character['Name']['text']}")
      
  
  return render(request, 'abyss_randomizer/index.html', {
    'characters': scraper.get_element_from_column('characters', 'Weapon', 'text')
  })

def get_table_info(request, table_name):
  return JsonResponse(scraper.get_formatted_table(table_name), safe=False)