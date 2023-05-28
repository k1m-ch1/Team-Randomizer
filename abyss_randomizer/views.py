from django.shortcuts import render
from django.http import JsonResponse

import requests
from .models import *
from . import scrape_data_from_web as scraper
import re
from functools import reduce
from operator import *


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
  

def is_same_set(query_set_a, query_set_b, comparison_attribute):
  converted_query_set_a = set(map( lambda x: getattr(x, comparison_attribute), query_set_a))
  converted_query_set_b = set(map(lambda x: getattr(x, comparison_attribute), query_set_b))
  
  print('converted set a:', converted_query_set_a)
  print('converted set b:', converted_query_set_b)
  return converted_query_set_a == converted_query_set_b
  


def add_update_or_pass_to_database(list_of_hr_formatted, table_class, base_keys, update_keys={}, many_to_many_keys=None):
  """
    table_name is the name of the table like 'characters', 'regions', ...
    table_class is the Model name of the table like Region, GenshinCharacters
    update_keys is a dictionary that will be passed as arguments where the key is a name of the column of the Model table. The value will be a higher order function that will have a formatted_hr passed in
    base_keys are the keys from update_keys that should be checked to prevent duplicates. For example if there's already a row for 'Traveler' but the new data has a different Element columns, we don't want another 'Traveler' row but instead we want to update the existing 'Traveler' row
  """
  # Note: the term new means the data extracted from the web meanwhile old refers to data that's already in the database
  for hr_formatted in list_of_hr_formatted:
    # hr_formatted is a dictionary. Ex: hr_formatted['Name']['text']
  
    temp_base_keys = {k: v(hr_formatted) for k, v in base_keys.items()}
    print([x for x in temp_base_keys.values()])
    new_row_non_rel = { k: v(hr_formatted) for k, v in update_keys.items()}
    print([x for x in new_row_non_rel.values()])
    # v(hr_formatted) will be some variable that will be passed into the database (final value)
    if many_to_many_keys is not None:
      new_row_rel = { k: v(hr_formatted) for k, v in many_to_many_keys.items()}
      # v(hr_formatted) will be a set that contains the many to many elements (final value)
    else:
      new_row_rel = None
    old_row = table_class.objects.filter(**temp_base_keys)
    
    
    def check_rel_fields_for_update():
      """
        Evaluates whether you should update the row. returns True if yes and False if no
      """
      if many_to_many_keys is None: return True
      for row in old_row:
        # print(row.element.all())
        [print('old set:',set(getattr(row, k).all())) == print('new set:',set(v)) for k, v in new_row_rel.items()]
        [print('is same set: ', is_same_set(set(getattr(row, k).all()), set(v), list(base_keys.keys())[0])) for k, v in new_row_rel.items()]
        print('reduce: ', reduce(and_, [is_same_set(set(getattr(row, k).all()), set(v), list(base_keys.keys())[0]) for k, v in new_row_rel.items()]))
        if reduce(and_, [is_same_set(set(getattr(row, k).all()), set(v), list(base_keys.keys())[0]) for k, v in new_row_rel.items()]):
          print('Has no difference')
          return False
  
      # for rows in table_class.objects.all():
        # if reduce(and_, [set(getattr(rows, k).all()) == v for k, v in new_row_rel.items()]):
      #  [print(getattr(rows, k)) == print(set(v)) for k, v in new_row_rel.items()]
          # return False
      print('Function will return true')
      return True
    
    print(len(table_class.objects.filter(**new_row_non_rel)) == 0, check_rel_fields_for_update())
    if len(old_row) == 0:
      # If doesn't exists previously create a new table
      
      new_row = table_class.objects.create(**temp_base_keys, **new_row_non_rel)
      if many_to_many_keys is not None:
        for k, v in new_row_rel.items():
          # print('k:',k,'\n', 'v:', v, '\n')
          # print('row:', new_row, '\n')
          getattr(new_row, k).add(*v)
      print(f'Created a new {table_class} called {new_row}')
      
      # Check whether there's already a row that contains an identifier value. Indentifier value example: name of character, name of element, ...
    elif len(table_class.objects.filter(**new_row_non_rel)) == 0 or ():
      
      
      # some field got changed

      old_row.update(**new_row_non_rel)
      if many_to_many_keys is not None:
        for k, v in new_row_rel.items():
          for row in old_row:
            getattr(row, k).add(*v)
      print(f'Updated a {table_class} table at {old_row}')
  


def index(request):
  weapons = scraper.get_formatted_table('weapons')
  regions = scraper.get_formatted_table('regions')
  characters = scraper.get_formatted_table('characters')
  
  add_update_or_pass_to_database(MODEL_TYPE, ModelType, {'name':lambda x: x})
  add_update_or_pass_to_database(weapons, WeaponType, 
                                 {'name': lambda x: x['Type']['text'][:-1]},
                                 {'icon_url':lambda x: x['Icon']['img_src']})
  add_update_or_pass_to_database(regions, ElementType, 
                                 {'name':lambda x: x['Element']['text']}, 
                                 {'icon_url': lambda x: x['Element']['img_src']})
  add_update_or_pass_to_database(characters, Rarity, 
                                 {'star':lambda x: int(re.search(r'.+Icon_([0-9])_Stars.png.+', x['Quality']['img_src']).group(1))}, 
                                 {'icon_url': lambda x: x['Quality']['img_src']})
  add_update_or_pass_to_database(regions, Region, 
                                 {'name': lambda x: x['Nation']['text']}, 
                                 {'icon_url': lambda x: x['Nation']['img_src'],
                                  'element': lambda x: get_object(ElementType, name=x['Element']['text'])})
  
  def handle_iter(x, lookup_table, col_name, data_attr, identifier):
    result = x[col_name][data_attr]
    # print(result)
    if type(result) == list:
      return {get_object(lookup_table, **{identifier:i}) for i in result}
    return {get_object(lookup_table, **{identifier:result})}
  
  add_update_or_pass_to_database(characters, GenshinCharacter, 
                                 {'name':lambda x: x['Name']['text']}, 
                                 {'character_url': lambda x: x['Icon']['img_src'],
                                  'weapon': lambda x: get_object(WeaponType, name=x['Weapon']['text']),
                                  'quality': lambda x: get_object(Rarity, star=int(re.search(r'.+Icon_([0-9])_Stars.png.+', x['Quality']['img_src']).group(1))),
                                  'region': lambda x: get_object(Region, name=x['Region']['text'])},
                                 many_to_many_keys={'element': lambda x: handle_iter(x, ElementType, 'Element', 'text', 'name'),
                                  'model_type': lambda x: handle_iter(x, ModelType, 'Model Type', 'text', 'name')})
  
  #     try:
  #       result_element = character['Element']['text']
  #       print(result_element)
  #       if type(result_element) == list:
  #         for element in result_element:
  #           new_character.element.add(get_object(ElementType, name=element))
  #       else:
  #           new_character.element.add(get_object(ElementType, name=result_element))
        
  #       result_model = character['Model Type']['text']
  #       print(result_model)
  #       if type(result_element) == list:
  #         for model in result_model:
  #           new_character.model_type.add(get_object(ModelType, name=model))
  #         else:
  #           new_character.model_type.add(get_object(ModelType, name=result_model))
        
  #       new_character.save()
  #     except:
  #       pass
  
  # for model_type in MODEL_TYPE:
  #   if len(ModelType.objects.filter(name=model_type)) == 0:
  #     ModelType(name=model_type).save()
  #     print(f"Created new object called {model_type}") 
  
  # for weapon in weapons:
  #   if len(WeaponType.objects.filter(name=weapon['Type']['text'][:-1])) == 0:
  #     WeaponType(name=weapon['Type']['text'][:-1], icon_url=weapon['Icon']['img_src']).save()
  #     print(f"Created new object called {weapon['Type']['text']}")
  
  # for element in regions:
  #   if len(ElementType.objects.filter(name=element['Element']['text'])) == 0:
  #     ElementType(name=element['Element']['text'], icon_url=element['Element']['img_src']).save()
  #     print(f"Created new object called {element['Element']['text']}")
      
  
  # for rarity in characters:
  #   if len(Rarity.objects.filter(star = int(re.search(r'.+Icon_([0-9])_Stars.png.+', rarity['Quality']['img_src']).group(1)))) == 0:
  #     Rarity(icon_url=rarity['Quality']['img_src'], star=int(re.search(r'.+Icon_([0-9])_Stars.png.+', rarity['Quality']['img_src']).group(1))).save()
  #     print(f"Created new object called {rarity['Quality']['img_src']}")

  
  # for region in regions:
  #   if len(Region.objects.filter(name=region['Nation']['text'])) == 0:
  #     Region(name=region['Nation']['text'], icon_url=region['Nation']['img_src'], element=ElementType.objects.get(name=region['Element']['text'])).save()
  #     print(f"Created new object called {region['Nation']['text']}")


  # for character in characters:
  #   if len(GenshinCharacter.objects.filter(name=character['Name']['text'])) == 0:
  #     new_character = GenshinCharacter.objects.create(name=character['Name']['text'],
  #                      character_url=character['Icon']['img_src'],
  #                      weapon=WeaponType.objects.get(name=character['Weapon']['text']),
  #                      quality=Rarity.objects.get(star=int(re.search(r'.+Icon_([0-9])_Stars.png.+', character['Quality']['img_src']).group(1))),
  #                      region=get_object(Region, name=character['Region']['text']))
  #     try:
  #       result_element = character['Element']['text']
  #       print(result_element)
  #       if type(result_element) == list:
  #         for element in result_element:
  #           new_character.element.add(get_object(ElementType, name=element))
  #       else:
  #           new_character.element.add(get_object(ElementType, name=result_element))
        
  #       result_model = character['Model Type']['text']
  #       print(result_model)
  #       if type(result_element) == list:
  #         for model in result_model:
  #           new_character.model_type.add(get_object(ModelType, name=model))
  #         else:
  #           new_character.model_type.add(get_object(ModelType, name=result_model))
        
  #       new_character.save()
  #     except:
  #       pass
      
  #     print(f"Created new object called {character['Name']['text']}")
      
  
  return render(request, 'abyss_randomizer/index.html', {
    'characters': scraper.get_element_from_column('characters', 'Weapon', 'text')
  })

def get_table_info(request, table_name):
  return JsonResponse(scraper.get_formatted_table(table_name), safe=False)