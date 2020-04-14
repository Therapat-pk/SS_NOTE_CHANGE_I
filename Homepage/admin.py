from django.contrib import admin
from .models import Lecture,Profile,Lecture_img

# Register your models here.
admin.site.register(Lecture)
admin.site.register(Profile)
admin.site.register(Lecture_img)