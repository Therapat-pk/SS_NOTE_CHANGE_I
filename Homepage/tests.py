import os
import glob
from pathlib import Path
from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import render,HttpResponse
from django.test import Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
from sandslecture.settings import BASE_DIR
from Homepage.models import *
from .forms import *

class SSNoteTest(TestCase):

    def setUp(self):  
        localtion_base=BASE_DIR
        user_default=User.objects.create_user(username='Timmy',password='2000')
        profile_default=Profile.objects.create(user=user_default)
        lecture_default=Lecture.objects.create(title="linux",description="about linux", author=profile_default)
        Lecture_image(lecturekey=lecture_default,
            image=SimpleUploadedFile('red.png', content=open(localtion_base+'/red.png', 'rb').read()))

    

    def test_create_new_model_profile(self):
        password = 'new_password'
        new_user = User.objects.create_user('new_user', password)
        new_profile = Profile()
        new_profile.user = new_user
        new_profile.save()
        self.assertEqual('new_user',new_profile.user.username)
        
    def test_saving_and_retrieving_lecture_title(self):
        first_lecture = Lecture()
        first_lecture.title = 'The first (ever) lecture title'
        first_lecture.save()

        second_lecture = Lecture()
        second_lecture.title = 'lecture title the second'
        second_lecture.save()

        lectures = Lecture.objects.all()
        self.assertEqual(lectures.count(), 2)

        first_lecture = lectures[0]
        second_lecture = lectures[1]
        self.assertEqual(first_lecture.title, 'The first (ever) lecture title')
        self.assertEqual(second_lecture.title, 'lecture title the second')

    def test_saving_lecture_id_auto_increment_start_at_1(self):
        first_lecture = Lecture()
        first_lecture.title = 'The first (ever) lecture title'
        first_lecture.save()

        second_lecture = Lecture()
        second_lecture.title = 'lecture title the second'
        second_lecture.save()

        lectures = Lecture.objects.all()
        self.assertEqual(lectures.count(), 2)

        first_lecture = lectures[0]
        second_lecture = lectures[1]
        self.assertEqual(first_lecture.id, 1)
        self.assertEqual(second_lecture.id, 2)

    def test_upload_pic_Profile(self):
        '''client = Client()
        profile_form = Profileform()
        localtion_base = BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        upload_profile = client.post('/profile/'+str(profile)+'/', 
            {'img_profile':SimpleUploadedFile('666.png', 
            content=open(localtion_base+'/red.png', 'rb').read())}) '''
        Count_object=Profile.objects.filter(id=1)[0].profile_picture 

        #with self.assertRaises(TypeError, Count_object)





    def test_submit_Lecture(self):
        
        
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        self.client.post('/upload/', {'title':'tim','description':"555",
            'image':SimpleUploadedFile('666.png',
            content=open(localtion_base+'/red.png', 'rb').read())}) 
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
        
        useA=noteObj.user_saved.add(userAProfile)
        
        self.assertEqual(noteObj.user_saved.count(),1)
        self.assertIn(userAProfile,Lecture.objects.all()[0].user_saved.all())
        useB=noteObj.user_saved.add(userBProfile)
        
        self.assertEqual(noteObj.user_saved.count(),2)
        self.assertIn(userBProfile,Lecture.objects.all()[0].user_saved.all())

    def test_search_Lecture(self):
        creator = User.objects.create_user(username = 'tim01',password = 'pass')
        creatorProfile = Profile.objects.create(user = creator)
        noteObj = Lecture.objects.create(title = 'test', description = 'test',author = creatorProfile)
        noteObj_Img=Lecture_image.objects.create(lecturekey=noteObj,image=SimpleUploadedFile('666_1.png', content=open(BASE_DIR+'/red.png', 'rb').read()))
        response = self.client.get('/',{'keyword_search':'test'})
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
        
    
    def test_error_case_none_parameter_in_reverse(self):
        localtion=BASE_DIR
        Tim=User.objects.create_user(username='Timmy',password='2542')
        ProfileTim=Profile.objects.create(user=Tim)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'timer','description':"timer_t" 
            ,'image':SimpleUploadedFile('666.png', content=open(localtion+'/red.png', 'rb').read())} )
        with self.assertRaises(Exception):
            HttpResponse(reverse("S&S:lecture"))
        



    def tearDown(self):
        #location=BASE_DIR+'/sandslecture'+'/media'
        #for i in 
        #os.remove(location+'/images'+'/')
        for i in glob.glob(BASE_DIR+'/sandslecture/media/*'):
            i=Path(i)
            for file in i.glob('666*.png'):
                os.remove(file)

        
        


       