from django.urls import path
from . import views

# for class based views, use <int:pk> instead of <int:cat_id>
# for function based views, use <int:cat_id> instead of <int:pk>
# pk stands for primary key
# for each route specified, you must have a view function
urlpatterns = [
  # url path for home page & about page
  path('', views.home, name='home'),
  path('about/', views.about, name='about'),
  # url path for trips CRUD
  path('trips/', views.TripIndex.as_view(), name='trips_index'),
  path('trips/<int:pk>/', views.TripDetail.as_view(), name='trips_detail'),
  path('trips/create/', views.TripCreate.as_view(), name='trips_create'),
  path('trips/<int:pk>/update/', views.TripUpdate.as_view(), name='trips_update'),
  path('trips/<int:pk>/delete/', views.TripDelete.as_view(), name='trips_delete'),
  # url path for add checklist, add activity, add photo, assoc destination
  path('add_checklist/<int:trip_id>/', views.add_checklist, name='add_checklist'),
  path('trips/<int:trip_id>/add_activity/', views.add_activity, name='add_activity'),
  # path('trips/<int:trip_id>/add_photo/', views.add_photo, name='add_trip_photo'),
  path('destinations/<int:destination_id>/add_photo/', views.add_photo, name='add_destination_photo'),
  path('destinations/<int:destination_id>/remove_photo/<int:photo_id>', views.remove_photo, name='remove_destination_photo'),
  path('checklist/complete/<int:checklist_id>/', views.mark_complete, name='mark_complete'),

  # path('trips/<int:trip_id>/assoc_destination/<int:destination_id>/', views.assoc_destination, name='assoc_destination'),

  path(
        'trips/<int:trip_id>/assoc_destination/<int:destination_id>/',
        views.assoc_destination,
        name='assoc_destination'
    ),
  path(
        'trips/<int:trip_id>/unassoc_destination/<int:destination_id>/',
        views.unassoc_destination,
        name='unassoc_destination'
    ),
  
  # url path for destinations CRUD
  path('destinations/', views.DestinationIndex.as_view(), name='destinations_index'),
  path('destinations/<int:pk>/', views.DestinationDetail.as_view(), name='destinations_detail'),
  path('destinations/create/', views.DestinationCreate.as_view(), name='destinations_create'),
  path('destinations/<int:pk>/update/', views.DestinationUpdate.as_view(), name='destinations_update'),
  path('destinations/<int:pk>/delete/', views.DestinationDelete.as_view(), name='destinations_delete'),
  # url path for signup
  path('accounts/signup/', views.signup, name='signup'),
  # testing
  path('trips/<int:trip_id>/add_destinations/', views.assoc_destination, name='add_destinations'),

]