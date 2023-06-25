import random
import string

def print_formatted_randomize_team(func):
  def inside(*args, **kwargs):
    ret_val = func(*args, **kwargs)
    print(f"""\n
          My args: {args}
          My kwargs: {kwargs}
          Ret_val: {ret_val}\n
          """)
    return ret_val
  return inside

# @print_formatted_randomize_team
def split_and_randomize_to_teams(list_to_randomize, team_length=None, number_of_teams=None):
  list_to_randomize = list_to_randomize.copy()
  len_of_list = len(list_to_randomize)
  random.shuffle(list_to_randomize)
  if number_of_teams is None and type(team_length) == int:
    number_of_teams = len(list_to_randomize) // team_length
  elif team_length is None and type(number_of_teams) == int:
    team_length = len(list_to_randomize) // number_of_teams
  elif type(team_length) == int and type(number_of_teams) == int:
    pass
  else: 
    return

  return [[list_to_randomize.pop() for i in range(team_length)] for j in range(number_of_teams)], list_to_randomize


if __name__ == '__main__':
  test_list = list(string.ascii_lowercase)
  split_and_randomize_to_teams(test_list, 5, 5)  
  split_and_randomize_to_teams(test_list, 10, None)
  split_and_randomize_to_teams(test_list, None, 10)
  split_and_randomize_to_teams(test_list, None, None)
  split_and_randomize_to_teams(test_list, 20, None)
  split_and_randomize_to_teams(test_list, 5, None)
  split_and_randomize_to_teams(test_list, 4, 5)
  split_and_randomize_to_teams(test_list, None, 3)
  split_and_randomize_to_teams(test_list, team_length=2, number_of_teams=None)
  split_and_randomize_to_teams(test_list, team_length=2)
  split_and_randomize_to_teams(test_list, number_of_teams=2)
  split_and_randomize_to_teams(test_list, 1000, None)
  
  
  
  
    
  
   
  
    