from django.urls import path

from . import views

app_name = 'custom_randomizer'

urlpatterns = [
    path('', views.index, name='index')
]
