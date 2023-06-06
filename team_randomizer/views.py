from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse


from django.urls import reverse

from abyss_randomizer.models import User, GenshinCharacter
import abyss_randomizer.genshin_info as genshin_info

def save_user_characters_to_models(user):
  all_characters = genshin_info.get_characters(user.uid, user.ltuid, user.ltoken)
  user.characters.clear()
  for character in all_characters:
    user.characters.add(GenshinCharacter.objects.get(name=character))
  user.save()

def require_login(func):
  def ret_func(*args, **kwargs):
    if args[0].user.is_authenticated:
      return func(*args, **kwargs)
    else:
      return HttpResponseRedirect(reverse('login'))
  return ret_func

def home(request):
  return render(request, 'team_randomizer/index.html')

def login_view(request):
  message = None
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      # return HttpResponseRedirect(reverse('abyss_randomizer'))
      message = {'message': "Login sucessful!", 'alert_class': 'alert-success'}
    else:
      message = {'message':"Failed to login. Please register if you don't have an account", 'alert_class': 'alert-danger'}
  return render(request, 'team_randomizer/login.html', {
    'message':message
  })

def register_view(request):
  message = None
  if request.method == 'POST':
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    reconformation = request.POST['password-conformation']
    if password == reconformation:
      try:
        user = User.objects.create_user(username, email, password)
        user.save()
        # return HttpResponseRedirect(reverse('abyss_randomizer'))
        message = {'message': "Registered successfully!",'alert_class':'alert-success'}
      except:
        message = {'message': "Username has already been taken", 'alert_class':  'alert-danger'}
        
    else:
      message = {'message': 'the passwords must match.', 'alert_class': 'alert-danger'}
  return render(request, 'team_randomizer/register.html', {
    'message': message
  })

def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse('home'))

@require_login
def user_profile(request):
  message = None
  user_obj = request.user
  if request.method == "POST":
    try:
      uid = int(request.POST['uid'])
      ltuid = int(request.POST['ltuid'])
      ltoken = request.POST['ltoken']
      if not genshin_info.is_valid_uid_ltuid_and_ltoken(uid, ltuid, ltoken):
        message = {'message': 'Invalid info', 'alert_class':'alert-danger'}
      else:
        user_obj.uid = int(request.POST['uid'])
        user_obj.ltuid = int(request.POST['ltuid'])
        user_obj.ltoken = request.POST['ltoken']
        user_obj.save()
        message = {'message' : 'Successfully saved user data!', 'alert_class':'alert-success'}
        print(f'Updated {user_obj.username}\'s ltuid as {user_obj.ltuid} and ltoken as {user_obj.ltoken}')
        save_user_characters_to_models(user_obj)
        print(f'{user_obj}\'s characters: {[print(i) for i in user_obj.characters.all()]}')
        
    except ValueError:
      message = {'message': 'Couldn\'t convert str to int', 'alert_class':'alert-danger'}
  return render(request, 'team_randomizer/user_profile.html', {
    'message': message,
    'your_characters': user_obj.characters.all()
  })

@require_login
def get_user_data(request):
  print(request.user.ltoken)
  if request.user.is_authenticated:
    user = User.objects.get(username=request.user.username)
    if (data:=genshin_info.is_valid_uid_ltuid_and_ltoken(user.uid, user.ltuid, user.ltoken)):
      return JsonResponse(data)
    else:
      return HttpResponse('Incorrect user information')


  
