from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

import requests
from .models import *
from . import scrape_data_from_web as scraper
import re
from functools import reduce
from operator import *
from . import genshin_info
import json


GENSHIN_CHARACTER_URL = 'https://genshin-impact.fandom.com/wiki/Character'
HEIGHT = ['Tall', 'Medium', 'Short']
GENDER = ['Male', 'Female']
MODEL_TYPE = reduce(add, (lambda x, y: list(map(lambda i: list(map(lambda j: i + ' ' + j, y)), x)))(HEIGHT, GENDER))


# Create your views here.

def get_object(django_table, **kwargs):
  """
    Is an alternative to the native element.objects.get(attr1="...")
    Doesn't return error if there isn't any element or if there are multiple elements.
  """
  try:
    result = django_table.objects.filter(**kwargs)
    if len(result) == 0:
      return None
    else:
      return result.first()
  except:
    return None

def filter_object(django_table, **kwargs):
  """
    Is an alternative to the native element.objects.filter(attr1="...", attr2="...",...)
    Returns None instead of empty set if no sign of element
  """
  try:
    result = django_table.objects.filter(**kwargs)
    if len(result) == 0:
      return None
    else:
      return result
  except:
    return None
  

def is_same_set(query_set_a, query_set_b, comparison_attribute):
  """
    Check whether a set is the same by comparing a base attribute with another set. 
    For example for a GenshinCharacter object, it will compare the name if the comparison attribute is "name"
  """
  converted_query_set_a = set(map( lambda x: getattr(x, comparison_attribute), query_set_a))
  converted_query_set_b = set(map(lambda x: getattr(x, comparison_attribute), query_set_b))

  return converted_query_set_a == converted_query_set_b
  


def add_update_or_pass_to_database(list_of_tr_formatted, table_class, base_keys, non_rel_keys={}, rel_keys=None):
  """
    list_of_tr_formatted should contain the list of table row that has been converted to a dictionary format
    table_name is the name of the table like 'characters', 'regions', ...
    table_class is the Model name of the table like Region, GenshinCharacters
    non_rel_keys is a dictionary that will be passed as arguments where the key is a name of the column of the Model table. The value will be a higher order function that will have a formatted_hr passed in
    base_keys are the keys that should be checked to prevent duplicates. For example if there's already a row for 'Traveler' but the new data has a different Element columns, we don't want another 'Traveler' row but instead we want to update the existing 'Traveler' row
    rel_keys are keys that are related in a ManyToManyField.
    Note: base_keys, the optional non_rel_keys and rel_keys should contain represent of the column of the table.
    base_keys, non_rel_keys and rel_keys are dictionary where the keys represent a column header of a table and the value is a higher order function to convert a tr_formatted to a data to be passed into the database.
  """
  # Note: the term new means the data extracted from the web meanwhile old refers to data that's already in the database
  for tr_formatted in list_of_tr_formatted:
    # tr_formatted is a dictionary. Ex: tr_formatted['Name']['text']
  
    converted_base_keys = {k: v(tr_formatted) for k, v in base_keys.items()}
    converted_non_rel_keys = { k: v(tr_formatted) for k, v in non_rel_keys.items()}
    # v(tr_formatted) will be some variable that will be passed into the database (final value)
    
    if rel_keys is not None:
      converted_rel_keys = { k: v(tr_formatted) for k, v in rel_keys.items()}
      # v(tr_formatted) will be a set that contains the many to many elements (final value)
    else:
      converted_rel_keys = None
    
    old_row = get_object(table_class, **converted_base_keys)
    
    def check_rel_fields_for_update():
      """
        Evaluates whether you should update the row. returns True if yes and False if no
        First checks whether the table has any rel_keys (many to many relationships) and returns a default value of False
        After that, checks whether there are any changes made to any of the row. (comparing new data from web to one that already exists in the database)
      """
      if rel_keys is None: return False
      no_attr_changed = reduce(and_, [reduce(and_, [is_same_set(set(getattr(old_row, k).all()), set(v), base_key) for base_key in base_keys.keys()]) for k, v in converted_rel_keys.items()])
      if not no_attr_changed:
        return True
      return False
    
    if old_row is None:
      # If doesn't exists previously create a new table
      
      new_row = table_class.objects.create(**converted_base_keys, **converted_non_rel_keys)
      if rel_keys is not None:
        for k, v in converted_rel_keys.items():
          getattr(new_row, k).add(*v)
      print(f'Created a new {table_class} called {new_row}')

    elif (a:=len(table_class.objects.filter(**converted_non_rel_keys)) == 0) or (b:=check_rel_fields_for_update()):
      # Check whether the row that already exists has the same converted_non_rel_keys and converted_rel_keys value
      print(f'non rel same: {not a}\nrel same: {not b}')
      # some field got changed
      
      for key_to_update, new_value in converted_non_rel_keys.items():
        setattr(old_row, key_to_update, new_value)
      if rel_keys is not None:
        for k, v in converted_rel_keys.items():
          getattr(old_row, k).add(*v)
          print('added: ', *v)
      old_row.save()
      print(f'Updated a {table_class} table at {old_row}')
  
def update_database():
  """
    updates the entire database based on data from the web
  """
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
    """
      In the Json you get from the scrapper module, many to many data is either represented as a list with different element in them or as an individual element if there's only one element.
      This function will convert the single element or the list to a set where it easily be manipulated.
      
      x is the tr_formatted you get from the scrapper module
    """
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
                                 rel_keys={'element': lambda x: handle_iter(x, ElementType, 'Element', 'text', 'name'),
                                  'model_type': lambda x: handle_iter(x, ModelType, 'Model Type', 'text', 'name')}) # in these rel_keys, the lambda function is just a util function
  

def index(request):
  try:
    update_database()
  except:
    pass
  return render(request, 'abyss_randomizer/index.html', {
    'characters': scraper.get_element_from_column('characters', 'Name', 'text')
  })

def get_table_info(request, table_name):
  return JsonResponse(scraper.get_formatted_table(table_name), safe=False)

def get_ltuid_and_ltoken(request):
  return JsonResponse(genshin_info.get_browser_cookies())

def get_all_characters(request):
  if request.method == 'GET':
    return JsonResponse({character.name:character.character_url for character in GenshinCharacter.objects.all()}, safe=False)
  return HttpResponseBadRequest()

def get_characters(request):
  return JsonResponse({character.name:character.character_url for character in request.user.characters.all()}, safe=False)

def get_character(request):
  if request.method == 'GET':
    try:
      character = GenshinCharacter.objects.get(name=request.GET['character-name'])
      return JsonResponse({character.name:character.character_url})
    except:
      return HttpResponseBadRequest('Character doesn\'t exist')


TABLE_DATA_MAPPER = {
  'elements': (ElementType, 'name', 'element', True),
  'weapons': (WeaponType, 'name', 'weapon', False),
  'rarity': (Rarity, 'star', 'quality', False),
  'region': (Region, 'name', 'region', False),
  'model type': (ModelType, 'name', 'model_type', True)
}

def filter_characters_from_db_single_attr(attr_name, chosen_attr, character_pool):
  """
    Filters only a single attribute from the data pool. Returns a list.
  """
  if len(chosen_attr) == 0 or len(character_pool) == 0:
    return []
  else:
    template_attr = TABLE_DATA_MAPPER[attr_name]
    first_attr = chosen_attr.pop()
    attr_for_comparison = get_object(template_attr[0], **{template_attr[1]:first_attr})
    
    def auto_compare_rel(attr_primary, attr_lookup):
      if template_attr[3]:
        # print(f'Attr "{attr_name}" lookup:', attr_lookup.all())
        return attr_primary in set(attr_lookup.all())
      else:
        # print(f'Attr {attr_name} lookup not many to many:', attr_lookup)
        return attr_primary == attr_lookup
    
    after_filtering = [character for character in character_pool if auto_compare_rel(attr_for_comparison, getattr(character, TABLE_DATA_MAPPER[attr_name][2]))]
    return  after_filtering + filter_characters_from_db_single_attr(attr_name, chosen_attr, character_pool)


def filter_characters_from_db(attr_to_use_as_li, character_pool):
  """
    attr_to_use_as_li is a list representation of a dictionary using dict.items() method. It represents the attributes in use, structure like one that's stored in the localstorage .
    character_pool is a set and contains all of the characters that will be filtered.
    returns a set of characters
  """

  if len(attr_to_use_as_li) == 0:
    return character_pool
  else:
    attr_name, chosen_attr = attr_to_use_as_li.pop()
    character_after_filter = filter_characters_from_db_single_attr(attr_name, chosen_attr, character_pool)
    # print('Character after filter: ', character_after_filter)
    ret_val = list(set(filter_characters_from_db(attr_to_use_as_li, character_after_filter)))
    # print('Attr name: ', attr_name)
    # print(ret_val)
    return ret_val
  

def get_character_schema(request):
  get_all_row_name = lambda table_class, attr: [str(getattr(table_row, attr)) for table_row in table_class.objects.all()]
  table_data = {key:get_all_row_name(value[0], value[1])+['None'] for key, value in TABLE_DATA_MAPPER.items()}
  return JsonResponse(table_data)

@csrf_exempt
def randomize(request):
  print('Request type:', type(request))
  print('Request:', request)
  print('Request methods:', dir(request))
  print('Request body:', request.body)
  print('Request GET:', request.POST)
  data = json.loads(request.body)
  return JsonResponse(data)
  
@csrf_exempt
def filter_characters(request):
  if request.method == 'POST':
    # try:
    loaded_table = json.loads(request.body)
    ret_val = filter_characters_from_db(list(loaded_table.items()), set(GenshinCharacter.objects.all()))
    
    return JsonResponse({char.name:char.character_url for char in ret_val}, safe=False)
    # except:
    #   return HttpResponseBadRequest(f"Wrong incorrect data")
  return HttpResponseBadRequest(f"Doesn't support {request.method} request, can only post")