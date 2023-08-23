from typing import Any, Dict
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Trips, Destinations, Photos, Checklist, Travelers, Activities
from .forms import ChecklistForm, ActivityForm, SignupForm, AddDestinationForm
from datetime import datetime
# import these for aws upload
import googlemaps
import requests, json
import uuid # this is to make random numbers
import boto3 # this is to make calls to aws
import os # os.environ['BUCKET_NAME'] is to read environment variables

gmaps = googlemaps.Client(key='AIzaSyCgRAHdFcRKhO-Qszsqpt_fOq4Q7wUMK8Y')

# Views for routes: '/' & '/about/'
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

# View for routes: Trips CRUD 
class TripIndex(LoginRequiredMixin, ListView): 
    model = Trips
    fields = '__all__'

    template_name = 'trip_index.html'
    context_object_name = 'trips'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        for trip in context['trips']:
            days_until = (trip.startDate - today).days
            trip.days_until = days_until

        return context
    


class TripDetail(LoginRequiredMixin, DetailView): 
    model = Trips
    fields = '__all__'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

         # Get the trip object from the context
        trip = context['object']
        
        # Get all destinations that are not associated with the trip
        not_associated_destinations = Destinations.objects.exclude(id__in=trip.destination_ids.all())
        
        # Pass the not_associated_destinations queryset to the template context
        context['not_associated_destinations'] = not_associated_destinations
        
        # Pass the associated destinations to the template context
        context['associated_destinations'] = trip.destination_ids.all()

        # Passing checklist form
        context['checklist_form'] = ChecklistForm()

        trip = context['object']
        context['checklists'] = Checklist.objects.filter(trip_id=trip)
        
        return context
    
    
class TripCreate(LoginRequiredMixin, CreateView): 
    model = Trips
    fields = ['name', 'startDate', 'endDate', 'budget']
    # this is to associate the user with the trip
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user
        # Let the CreateView do its job as usual
        return super().form_valid(form)
    
class TripUpdate(LoginRequiredMixin, UpdateView): 
    model = Trips
    fields = ['name', 'startDate', 'endDate', 'budget']

class TripDelete(LoginRequiredMixin, DeleteView): 
    model = Trips
    success_url = '/trips/'

# View for routes: Destinations CRUD
class DestinationIndex(LoginRequiredMixin, ListView): 
    model = Destinations
    fields = '__all__'
    
class DestinationDetail(LoginRequiredMixin, DetailView): 
    model = Destinations
    fields = '__all__'
    
    def get_location_details(self, name, country):
        locdata = gmaps.geocode(f'{name}, {country}')
        latlong = list(locdata[0]['geometry']['location'].values())
        lat = latlong[0]
        long = latlong[1]
        return lat, long
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = self.object.name
        country = self.object.country
        lat, long = self.get_location_details(name, country)
        timezone = gmaps.timezone((lat, long))
        context['timezone'] = timezone
        return context
    

class DestinationCreate(LoginRequiredMixin, CreateView): 
    model = Destinations
    fields = ['name', 'country', 'language', 'currency']
    
class DestinationUpdate(LoginRequiredMixin, UpdateView): 
    model = Destinations
    fields = ['name', 'country', 'language', 'currency']
    
class DestinationDelete(LoginRequiredMixin, DeleteView): 
    model = Destinations
    success_url = '/destinations/'

# View for routes: add checklist, add activity, add photo, assoc destination
@login_required
def add_checklist(request, trip_id):
    trip = get_object_or_404(Trips, pk=trip_id)
    print(trip)
    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        print(form.data)
        if form.is_valid():
            checklist = form.save(commit=False)
            checklist.trip = trip  # Assign the trip instance
            checklist.save()
            return redirect('trips_detail', pk=trip_id)

    # If there's a problem with the form or request method
    return redirect('trips_detail', pk=trip_id)

@login_required
def add_activity(request, destination_id):
    form = ActivityForm(request.POST)
    if form.is_valid():
        new_activity = form.save(commit=False)
        new_activity.destination_id = destination_id
        new_activity.save()
    return redirect('trips_detail', pk=destination_id)

# @login_required
# def assoc_destination(request, trip_id, destination_id):
#     Trips.objects.get(id=trip_id).destination_ids.add(destination_id)
#     return redirect('trips_detail', pk=trip_id)

@login_required
def assoc_destination(request, trip_id, destination_id):
    trip = get_object_or_404(Trips, id=trip_id)
    destination = get_object_or_404(Destinations, id=destination_id)
    trip.destination_ids.add(destination)
    return redirect('trips_detail', pk=trip_id)
    # if request.method == 'POST':
    #     print(request.POST)
    #     print(trip_id)
    #     form = AddDestinationForm(request.POST, instance=trip)
    #     if form.is_valid():
    #         form.save()
            
    #     return redirect('trips_detail', pk=trip_id)
    # else:
    #     form = AddDestinationForm(instance=trip)
    
    # return render(request, 'main_app/assoc_destinations.html', {'form': form, 'trip': trip})

@login_required
def unassoc_destination(request, trip_id, destination_id):
    trip = get_object_or_404(Trips, id=trip_id)
    destination = get_object_or_404(Destinations, id=destination_id)
    trip.destination_ids.remove(destination)
    return redirect('trips_detail', pk=trip_id)

# stubbing up functions for photo upload for now
@login_required
def add_photo(request, destination_id):
    # pull the photo from the form
    destination = Destinations.objects.get(id=destination_id)
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        #initialize s3 connection
        s3 = boto3.client('s3')
        # generate a unique id for the photo
        # photo_file.name[photo_file.name.rfind('.'):] is to get the file extension)
        key = 'wanderlust/' + uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            # access the bucket
            bucket = os.environ['BUCKET_NAME']
            # upload the photo to s3
            s3.upload_fileobj(photo_file, bucket, key)
            # build the url for the photo
            url = f'{os.environ["S3_BASE_URL"]}{bucket}/{key}'
            print(url)
            # create a photo in the db
            Photos.objects.create(url=url, destination_id=destination)
        # save url to the photo model + add fk for trip_id or destination_id
        except Exception as err:
            print(err)
            print('An error occurred uploading file to S3')
    
    return redirect('destinations_detail', pk=destination_id)

# View for routes: login, signup, logout
def signup(request):
    error_message = ''
    
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = SignupForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('trips_index')
        else:
            error_message = 'Invalid sign up - try again'
            
    # A bad POST or a GET request, so render signup.html with an empty form
    form = SignupForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)

@login_required
def mark_complete(request, checklist_id):
    checklist = get_object_or_404(Checklist, pk=checklist_id)
    checklist.complete = True
    checklist.save()
    return redirect('trips_detail', pk=checklist.trip_id)




    