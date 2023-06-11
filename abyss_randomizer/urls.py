from django.urls import path


from . import views

app_name = 'abyss_randomizer' 

urlpatterns = [
    path('', views.index, name="index"),
    path('tables/<str:table_name>', views.get_table_info, name="get_tables"),
    path('get-all-characters/', views.get_all_characters, name='get_all_characters'),
    path('get-ltuid-ltoken/', views.get_ltuid_and_ltoken, name='get_ltuid_ltoken'),
    path('get-characters', views.get_characters, name='get_characters'),
    path('get-character', views.get_character, name='get_character'),
    path('get-all-tables', views.get_all_tables, name='get_all_tables')
]
