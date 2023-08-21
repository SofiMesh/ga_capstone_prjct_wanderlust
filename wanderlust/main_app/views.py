from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Trips, Destinations, Photos, Checklist, Travelers, Activities
from .forms import ChecklistForm, ActivityForm

# import these for aws upload
import uuid # this is to make random numbers
import boto3 # this is to make calls to aws
import os # os.environ['BUCKET_NAME'] is to read environment variables

# Views for routes: '/' & '/about/'
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

# View for routes: Trips CRUD 
class TripIndex(LoginRequiredMixin, ListView): 
    model = Trips
    fields = '__all__'
     
class TripDetail(LoginRequiredMixin, DetailView): 
    model = Trips
    fields = '__all__'
    
class TripCreate(LoginRequiredMixin, CreateView): 
    model = Trips
    fields = ['name', 'startDate', 'endDate', 'budget', 'destination_ids']
    # this is to associate the user with the trip
    def form_valid(self, form):
        # Assign the logged in user (self.request.user)
        form.instance.user = self.request.user
        # Let the CreateView do its job as usual
        return super().form_valid(form)
    
class TripUpdate(LoginRequiredMixin, UpdateView): 
    model = Trips
    fields = ['name', 'startDate', 'endDate', 'budget', 'destination_ids']

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
    form = ChecklistForm(request.POST)
    if form.is_valid():
        new_checklist = form.save(commit=False)
        new_checklist.trip_id = trip_id
        new_checklist.save()
    return redirect('trips_detail', pk=trip_id)

@login_required
def add_activity(request, destination_id):
    form = ActivityForm(request.POST)
    if form.is_valid():
        new_activity = form.save(commit=False)
        new_activity.destination_id = destination_id
        new_activity.save()
    return redirect('trips_detail', pk=destination_id)

@login_required
def assoc_destination(request, trip_id, destination_id):
    Trips.objects.get(id=trip_id).destination_ids.add(destination_id)
    return redirect('trips_detail', pk=trip_id)

# stubbing up functions for photo upload for now
@login_required
def add_trip_photo(request, trip_id):
    return redirect('trips_detail', pk=trip_id)
        
@login_required
def add_destination_photo(request, destination_id):
    return redirect('destinations_detail', pk=destination_id)


# View for routes: login, signup, logout
def signup(request):
    error_message = ''
    if request.method == 'POST':
        # This is how to create a 'user' form object
        # that includes the data from the browser
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # This will add the user to the database
            user = form.save()
            # This is how we log a user in via code
            login(request, user)
            return redirect('trips_index')
        else:
            error_message = 'Invalid sign up - try again'
    # A bad POST or a GET request, so render signup.html with an empty form
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)



    
    