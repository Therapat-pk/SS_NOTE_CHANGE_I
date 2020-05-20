from django.db import models
from django.conf import settings
from django.contrib.auth.models import User


class Profile(models.Model): #It use to identify person (who is post or save this note)
    #user is link to User(Model by Django) #One User One profile
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        blank=True, default=None, null=True
        )

    #profile_picture 
    #Your can find it in Homepage/media/images
    profile_picture = models.ImageField(
        upload_to="images/", blank=True,
        default=None, null=True
        ) 
    
    #It show username when something call class Profile
    def __str__(self):
        return self.user.username

class Lecture(models.Model): #It is collect a content of note
    title = models.CharField(max_length=200, null=True ,blank=True)

    subject = models.CharField(max_length=200, null=True)

    description = models.CharField(max_length=2000, null=True)

    #author #It is link to Profile Class(It can be many Lecture on one Profile) 
    #!!!When use Check about Save()!!!
    #line(42-46)
    author = models.ForeignKey(
        Profile, related_name='author',
        on_delete=models.CASCADE, blank=True,
        null=True
        )

    #user_saved 
    #Ex Time(user 1) and Ace(user 2) are save C++ note and python note 
    #   user_saved(C++ note)have 2 Profile(Time and Ace) and Profile(Time)have 2 user_saved(C++ note and python note)
    # !!!When use Check about Save() !!!
    #There are many objects created. May be confused in order and adding models later.
    #Ex I create One Lecture ,I'am save() or save(commit=False) to create a Lecture_image but don't save() again 
    #   Server run pass Until when create a lecture we will know that it is Error if we don't use testing in Django
    user_saved = models.ManyToManyField(Profile) 

    #It show title when something call class Lecture
    def __str__(self):
        return self.title

class Lecture_image(models.Model):#It is collect a content picture on note

    #lecturekey 
    # It is link to Lecture Class(It can be many Lecture_image on one Lecture) 
    # !!!When use Check about Save() (line 42-44) !!!
    lecturekey = models.ForeignKey(
        Lecture, related_name='Lecture_image',
        on_delete=models.CASCADE, blank=True,
        null=True
        )

    image = models.ImageField(upload_to='lecture_image', )

    #It show name of image file when something call class Lecture_image
    def __str__(self):
        return self.image.name
    
class Rate(models.Model):
    user_rate=models.ForeignKey(Profile,
        on_delete=models.CASCADE, blank=True,
        null=True
        )
    lecture_rate=models.ForeignKey(Lecture,
        on_delete=models.CASCADE, blank=True,
        null=True
        )
    comment=models.CharField(max_length=1000,blank=True,
        null=True)
    rate=models.IntegerField(blank=True,
        null=True)

class ErrorReport(models.Model):
    error_views = models.CharField(max_length=100, null=True)
    error_detail = models.CharField(max_length=1000, null=True)
    error_massage_to_user= models.CharField(max_length=1000, null=True)

    
