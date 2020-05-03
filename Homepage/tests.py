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
from Homepage.models import Profile,Lecture,Lecture_image
from .forms import Profileform,LectureForms,Lecture_imgForms

class SSNoteTest(TestCase):

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

    def test_submit_lecture(self):      
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        self.client.post('/upload/', {'title':'tim','description':"555",
            'image':SimpleUploadedFile('666.png',
            content=open(localtion_base+'/red.png', 'rb').read())}) 
        count_lecture=Lecture.objects.count()
        count_lecture_image=Lecture_image.objects.count()
        
        self.assertEqual(count_lecture,1)
        self.assertEqual(count_lecture_image,1)


    def test_upload_muti_pic_lecture(self):
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='time',password='pass')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'time','password':"pass" } ) 
        self.client.post('/upload/', {'submitbutton':'Submit','title':'time','description':"555",
            'image':{SimpleUploadedFile('666_1.png', content=open(localtion_base+'/red.png', 'rb').read()),
            SimpleUploadedFile('666_1.png', content=open(localtion_base+'/red.png', 'rb').read())}} )
        
        self.assertEqual(Lecture.objects.count(),1)
        self.assertEqual(Lecture_image.objects.count(),2)

    
    def test_saves_lecture(self):
        creator = User.objects.create_user(username = 'tim_1',password = 'pass')
        userA = User.objects.create_user(username = 'timA',password = 'pass')
        userB = User.objects.create_user(username = 'timB',password = 'pass')
        creator_profile = Profile.objects.create(user = creator)
        userA_profile = Profile.objects.create(user = userA)
        userB_profile = Profile.objects.create(user = userB)
        note_obj = Lecture.objects.create(title = 'test', description = 'test',author = creator_profile)
        useA=note_obj.user_saved.add(userA_profile)

        self.assertEqual(note_obj.user_saved.count(),1)
        self.assertIn(userA_profile,Lecture.objects.all()[0].user_saved.all())

        useB=note_obj.user_saved.add(userB_profile)

        self.assertEqual(note_obj.user_saved.count(),2)
        self.assertIn(userB_profile,Lecture.objects.all()[0].user_saved.all())

    def test_search_lecture(self):
        creator = User.objects.create_user(username = 'tim_1',password = 'pass')
        creator_profile = Profile.objects.create(user = creator)
        note_obj = Lecture.objects.create(title = 'test', description = 'test',author = creator_profile)
        note_obj_Img=Lecture_image.objects.create(lecturekey=note_obj,image=SimpleUploadedFile('666_1.png',
            content=open(BASE_DIR+'/red.png', 'rb').read()))
        response = self.client.get('/',{'keyword_search':'test'})
        decode=response.content.decode()

        self.assertEqual(response.status_code,200)
        self.assertIn('test',decode)

    def test_change_password(self):
        creator = User.objects.create_user(username = 'tim_1',password = 'pass')
        creator_profile = Profile.objects.create(user = creator)
        self.client.login(username = 'tim_1',password = 'pass')
        self.client.post('/change-password/',{"old_password":'pass',"new_password1":"time25422542",
            "new_password2":"time25422542"})
        self.client.logout()
        Login_test_new_pass=self.client.post('/accounts/login/', {'username':'tim_1',
            'password':"time25422542" },follow=True ) 
        
        self.assertEqual(Login_test_new_pass.status_code,200)
        self.assertIn("tim_1",Login_test_new_pass.content.decode())
    
    def test_Lecture_show_on_home(self):
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'tim','description':"555" ,
            'image':SimpleUploadedFile('666.png', content=open(localtion_base+'/red.png', 'rb').read())} ) 
        home=self.client.post('/').content.decode()

        self.assertIn('666.png',home)
        self.assertIn('user',home)
        #self.assertEqual(Count_object,1)

    def test_Lecture_show_on_Profile(self):    
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'user','description':"555" ,
            'image':SimpleUploadedFile('666.png', content=open(localtion_base+'/red.png', 'rb').read())} ) 
        profile_page=Client().post('/profile/Timmy/',follow=True).content.decode()

        self.assertIn('666.png',profile_page)
        self.assertIn('user',profile_page)
        
    def test_error_case_none_parameter_in_reverse(self):
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        upload=self.client.post('/upload/', {'title':'timer','description':"timer_t" 
            ,'image':SimpleUploadedFile('666.png', content=open(localtion_base+'/red.png', 'rb').read())} )
        
        with self.assertRaises(Exception):
            HttpResponse(reverse("S&S:lecture"))

    def tearDown(self):
        for i in glob.glob(BASE_DIR+'/sandslecture/media/*'):
            i=Path(i)
            for file in i.glob('666*.png'):
                os.remove(file)

        
        


       