from django.forms import ModelForm
from .models import Checklist, Activities

class ChecklistForm(ModelForm):
  class Meta:
    model = Checklist
    fields = ['todos', 'complete']

class ActivityForm(ModelForm):
    class Meta:
        model = Activities
        fields = ['plannedAct', 'endDate', 'dueDate']