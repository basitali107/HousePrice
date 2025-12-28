# floor_map/urls.py
from django.urls import path
from . import views

app_name = 'floor_map'

urlpatterns = [
        path('', views.floor_map_input, name='home'),  # Make this the home page of the app
    path('floor-map/', views.floor_map_input, name='floor-map'),  # THIS IS REQUIRED

    path('', views.floor_map_input, name='floor_map_input'),
    path('', views.floor_map_input, name='floor-map'),  # home page
    path('floor-map/', views.floor_map_input),          # optional alias
]