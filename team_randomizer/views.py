from django.shortcuts import render


def home(request):
  return render(request, 'team_randomizer/index.html')