from django.urls import path


from . import views

app_name = 'abyss_randomizer' 

urlpatterns = [
    path('', views.index, name="index"),
    path('tables/<str:table_name>', views.get_table_info, name="get_tables")
]
