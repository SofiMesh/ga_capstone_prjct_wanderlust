from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Trips, Destinations, Photos, Checklist, Travelers, Activities
from .forms import ChecklistForm, ActivityForm, SignupForm, AddDestinationForm

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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = Destinations.objects.all() # or any other query you want
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

# @login_required
# def assoc_destination(request, trip_id, destination_id):
#     Trips.objects.get(id=trip_id).destination_ids.add(destination_id)
#     return redirect('trips_detail', pk=trip_id)

@login_required
def assoc_destination(request, trip_id):
    trip = Trips.objects.get(id=trip_id)
    if request.method == 'POST':
        print(request.POST)
        print(trip_id)
        form = AddDestinationForm(request.POST, instance=trip)
        if form.is_valid():
            form.save()
            
        return redirect('trips_detail', pk=trip_id)
    else:
        form = AddDestinationForm(instance=trip)
    
    return render(request, 'main_app/assoc_destinations.html', {'form': form, 'trip': trip})

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

