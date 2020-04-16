from django.db import models
from django.conf import settings
from django.contrib.auth.models import User



class Profile(models.Model): #It use to identify person (who is post or save this note)
    #user is link to User(Model by Django) #One User One profile
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        null=True
    )
    #ProfilePicture 
    #Your can find it in Homepage/media/images
    profilePicture = models.ImageField(upload_to="images/", blank=True, default=None, null=True) 
    
    #It show username when something call class Profile
    def __str__(self):
        return self.user.username

class Lecture(models.Model): #It is collect a content of note
    title = models.CharField(max_length=200,null=True)
    subject = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=2000,null=True)
    #author #It is link to Profile Class(It can be many Lecture on one Profile) #!!!When use Check about Save()
    author = models.ForeignKey(Profile, related_name='author',on_delete=models.CASCADE,blank=True,null=True)
    #userSaved #It can be many Profile on one userSaved and many userSaved on one Profile #!!!When use Check about Save()
    userSaved = models.ManyToManyField(Profile) 
    #It show title when something call class Lecture
    def __str__(self):
        return self.title

class Lecture_image(models.Model):#It is collect a content picture on note
    #lectureKey #It is link to Lecture Class(It can be many Lecture_image on one Lecture) #!!!When use Check about Save()
    lectureKey = models.ForeignKey(Lecture, related_name='Lecture_image',on_delete=models.CASCADE,blank=True,null=True)
    image = models.ImageField(upload_to='lecture_image',blank=True)
    #It show name of image file when something call class Lecture_image
    def __str__(self):
        return self.image.name

    
