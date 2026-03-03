# maps/urls.py
from django.urls import path
from . import views
from .views import resolve_qr_location
app_name = 'maps'

urlpatterns = [
    # we'll add URLs here later, for now keep it empty
     path('locations/', views.locations_list, name='locations'),
     path("api/resolve-location/", resolve_qr_location, name="resolve_qr_location"),
    path('route/', views.shortest_route, name='shortest_route'),
     path('edges/', views.edges_list, name='edges'),
    path('add_node/', views.add_node, name='add_node'),
    path('add_edge/', views.add_edge, name='add_edge'),
     path('update_node/', views.update_node, name='update_node'),
]
