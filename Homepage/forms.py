from django.forms import ModelForm
from .models import *

# Create the form class.
class Profileform(ModelForm):
     class Meta:
        model = Profile
        fields = ['profile_picture']

class LectureForms(ModelForm):
   class Meta:
      model = Lecture
      fields = ['title','description']

class Lecture_imgForms(ModelForm):
      class Meta:
         model = Lecture_image
         fields = ['image']