from Homepage.models import *
from django.contrib.auth.models import User
from django.shortcuts import render
from django.test import TestCase
from .forms import *
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client
from django.core.files import File
from sandslecture.settings import BASE_DIR
import os
from pathlib import Path
import glob

class HomePageTest(TestCase):

    def test_adding_new_model_Profile(self):
        password = 'newPassword'
        newUser = User.objects.create_user('newUser', password)
        newProfile = Profile()
        newProfile.user = newUser
        newProfile.save()
        self.assertEqual('newUser',newProfile.user.username)
        
    def test_saving_and_retrieving_lecture_title(self):
        firstLecture = Lecture()
        firstLecture.title = 'The first (ever) lecture title'
        firstLecture.save()

        secondLecture = Lecture()
        secondLecture.title = 'lecture title the second'
        secondLecture.save()

        lectures = Lecture.objects.all()
        self.assertEqual(lectures.count(), 2)

        firstLecture = lectures[0]
        secondLecture = lectures[1]
        self.assertEqual(firstLecture.title, 'The first (ever) lecture title')
        self.assertEqual(secondLecture.title, 'lecture title the second')

    def test_saving_lecture_id_auto_increment_start_at_1(self):
        firstLecture = Lecture()
        firstLecture.title = 'The first (ever) lecture title'
        firstLecture.save()

        secondLecture = Lecture()
        secondLecture.title = 'lecture title the second'
        secondLecture.save()

        lectures = Lecture.objects.all()
        self.assertEqual(lectures.count(), 2)

        firstLecture = lectures[0]
        secondLecture = lectures[1]
        self.assertEqual(firstLecture.id, 1)
        self.assertEqual(secondLecture.id, 2)

    def test_upload_pic_Profile(self):
        c = Client()
        form=Profileform()
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=Tim)
        response = c.post('/profile/'+str(ProfileTim)+'/', {'profilePicture':SimpleUploadedFile('666.png', content=open(localtion+'/red.png', 'rb').read())} ) 
        Count_object=Profile.objects.filter(id=1)[0].profilePicture 

        self.assertNotEquals(Count_object,"<ImageFieldFile: None>")





    def test_submit_Lecture(self):
        c = Client()
        
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=Tim)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        self.client.post('/upload/', {'title':'tim','description':"555" ,'image':SimpleUploadedFile('666.png', content=open(localtion+'/red.png', 'rb').read())} ) 
        CountLec=Lecture.objects.count()
        Count_object=Lecture_image.objects.count()

        self.assertEqual(CountLec,1)
        self.assertEqual(Count_object,1)


    def test_upload_Muti_Pic_Lecture(self):
        c=Client()
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='tim',password='pass')
        ProfileTim=Profile.objects.create(user=Tim)

        self.client.post('/accounts/login/', {'username':'tim','password':"pass" } ) 
        self.client.post('/upload/', {'submitbutton':'Submit','title':'tim','description':"555" ,'image':{SimpleUploadedFile('666_1.png', content=open(localtion+'/red.png', 'rb').read()),SimpleUploadedFile('666_1.png', content=open(localtion+'/red.png', 'rb').read())}} )
        self.assertEqual(Lecture.objects.count(),1)
        self.assertEqual(Lecture_image.objects.count(),2)

    
    def test_saves_Lecture(self):
        creator = User.objects.create_user(username = 'tim01',password = 'pass')
        userB = User.objects.create_user(username = 'tim21',password = 'pass')
        userA = User.objects.create_user(username = 'tim11',password = 'pass')
        creatorProfile = Profile.objects.create(user = creator)
        
        userAProfile = Profile.objects.create(user = userA)
        
        userBProfile = Profile.objects.create(user = userB)
        noteObj = Lecture.objects.create(title = 'test', description = 'test',author = creatorProfile)
        
        useA=noteObj.userSaved.add(userAProfile)
        
        self.assertEqual(noteObj.userSaved.count(),1)
        self.assertIn(userAProfile,Lecture.objects.all()[0].userSaved.all())
        useB=noteObj.userSaved.add(userBProfile)
        
        self.assertEqual(noteObj.userSaved.count(),2)
        self.assertIn(userBProfile,Lecture.objects.all()[0].userSaved.all())

    def test_search_Lecture(self):
        creator = User.objects.create_user(username = 'tim01',password = 'pass')
        creatorProfile = Profile.objects.create(user = creator)
        noteObj = Lecture.objects.create(title = 'test', description = 'test',author = creatorProfile)
        noteObj_Img=Lecture_image.objects.create(lectureKey=noteObj,image=SimpleUploadedFile('666_1.png', content=open(BASE_DIR+'/red.png', 'rb').read()))
        response = self.client.get('/',{'word':'test'})
        y=response.content.decode()

        self.assertEqual(response.status_code,200)
        self.assertIn('test',y)
    def test_change_password(self):
        creator = User.objects.create_user(username = 'tim01',password = 'pass')
        creatorProfile = Profile.objects.create(user = creator)
        self.client.login(username = 'tim01',password = 'pass')
        #self.client.post('/accounts/login/', {'username':'tim01','password':"pass" } ) 
        self.client.post('/change-password/',{"old_password":'pass',"new_password1":"time25422542","new_password2":"time25422542"})
        self.client.logout()
        Login_test_new_pass=self.client.post('/accounts/login/', {'username':'tim01','password':"time25422542" },follow=True ) 
        
        self.assertEqual(Login_test_new_pass.status_code,200)
        self.assertIn("tim01",Login_test_new_pass.content.decode())

    
    def test_Lecture_show_on_home(self):
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=Tim)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'tim','description':"555" ,'image':SimpleUploadedFile('666.png', content=open(localtion+'/red.png', 'rb').read())} ) 

        home=self.client.post('/').content.decode()

        self.assertIn('666.png',home)
        self.assertIn('tim',home)
        #self.assertEqual(Count_object,1)

    def test_Lecture_show_on_Profile(self):    
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=Tim)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'tim','description':"555" ,'image':SimpleUploadedFile('666.png', content=open(localtion+'/red.png', 'rb').read())} ) 
        Profile_page=Client().post('/profile/Timmy/',follow=True).content.decode()

        self.assertIn('666.png',Profile_page)
        self.assertIn('tim',Profile_page)

    def tearDown(self):
        #location=BASE_DIR+'/sandslecture'+'/media'
        #for i in 
        #os.remove(location+'/images'+'/')
        for i in glob.glob(BASE_DIR+'/sandslecture/media/*'):
            i=Path(i)
            for file in i.glob('666*.png'):
                os.remove(file)

        
        


       