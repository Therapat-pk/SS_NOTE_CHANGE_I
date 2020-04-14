from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        blank=True,
        default=None,
        null=True
    )
    profilePicture = models.ImageField(upload_to="images/", blank=True, default=None, null=True)
    def __str__(self):
        return self.user.username

class Lecture(models.Model):
    title = models.CharField(max_length=200,null=True)
    subject = models.CharField(max_length=200,null=True)
    description = models.CharField(max_length=2000,null=True)
    author = models.ForeignKey(Profile, related_name='author',on_delete=models.CASCADE,blank=True,null=True)
    userSaved = models.ManyToManyField(Profile)
    def __str__(self):
        return self.title

class Lecture_img(models.Model):
    LectureKey = models.ForeignKey(Lecture, related_name='Lecture_img',on_delete=models.CASCADE,blank=True,null=True)
    image = models.ImageField(upload_to='lecture_image',blank=True)
    def __str__(self):
        return self.image.name

    
