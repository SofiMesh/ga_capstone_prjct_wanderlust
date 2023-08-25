from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Checklist, Activities, User, Trips, Destinations, Travelers
from django.contrib.auth.models import User

class ChecklistForm(forms.ModelForm):
    class Meta:
        model = Checklist
        fields = ['todos', 'complete']
        labels = {
            'todos': '',  # Set the label to an empty string
            'complete': '',  # Set the label to an empty string
        }

class ActivityForm(ModelForm):
    class Meta:
        model = Activities
        fields = ['plannedAct', 'endDate', 'dueDate']

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        
class AddDestinationForm(forms.ModelForm):
    class Meta:
        model = Trips
        exclude = ['name', 'startDate', 'endDate', 'budget', 'user']
        widgets = {'destination_ids': forms.CheckboxSelectMultiple} 

class InvitationForm(forms.ModelForm):
    class Meta:
        model = Trips # this is the model we're trying to add data to
        fields = ['accepted_users'] # this is the field it's adding to in the Trips model
        widgets = {'accepted_users': forms.CheckboxSelectMultiple}