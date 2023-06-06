import genshinstats as gs

def get_characters(uid, ltuid, ltoken):
  if is_valid_uid_ltuid_and_ltoken(uid, ltuid, ltoken):
      gs.set_cookie(ltuid=ltuid, ltoken=ltoken)
      data = gs.get_user_stats(uid)
      return [x['name'] for x in data['characters']]


def is_valid_uid_ltuid_and_ltoken(uid, ltuid, ltoken):
  try:
    gs.set_cookie(ltuid=ltuid, ltoken=ltoken)
    data = gs.get_user_stats(uid)
    return data
  except:
    return False

def get_browser_cookies():
  return gs.get_browser_cookies()

if __name__ == '__main__':
  print(get_characters(838667071, 159767329, "xnel1urP6XicBnhioSAMDbE6p4pbWY9WYmsS8Cgj"))
  