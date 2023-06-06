"""
URL configuration for team_randomizer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'team_randomizer'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('abyss-randomizer/', include('abyss_randomizer.urls', namespace='abyss_randomizer'), name='abyss_randomizer'),
    path('custom-randomizer/', include('custom_randomizer.urls', namespace='custom_randomizer'), name='custom_randomizer'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('user-profile/', views.user_profile, name='user_profile'),
    path('get-user-data/', views.get_user_data, name='get_user_data'),
    path('', views.home, name='home')
]
