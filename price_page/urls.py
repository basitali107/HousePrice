# price_page/urls.py
from django.urls import path
from .views import price_page_view
from . import views


urlpatterns = [
    path('', price_page_view, name='price_page'),  # This will map /price-page/ to the view
    #  path('properties/', views.properties_list, name='properties_list'),
    path('property/<slug:slug>/', views.property_detail, name='property_detail'),  # ✅ This is required
]
