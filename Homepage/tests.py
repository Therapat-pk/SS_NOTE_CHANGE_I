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
        
    def test_error_case_data_upload(self):
        localtion_base=BASE_DIR
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        self.client.post('/accounts/login/', {'username':'Timmy','password':"2542" } ) 
        #wrong input 
        #nodata is empty data
        #no_image is no image in form lecture
        #image is only image in form lecture
        data_test = {'nodata':{},
            'no_image':{'title':'user','description':"555" },
            'image':{'image':SimpleUploadedFile('666.png', 
                                                content=open(localtion_base+'/red.png', 'rb').read())}
            }
        #correct input
        data_all_input = {'title':'user', 'description':"555", 
                          'image':SimpleUploadedFile('666.png', 
                                                     content=open(localtion_base+'/red.png', 'rb').read())
                          }
        for i in data_test: 
            
            #it will pass in which wrong input 
            upload=self.client.post('/upload/', data_test[i] )
            count_lecture=Lecture.objects.all().count()
            self.assertEqual(0,count_lecture)

        #test correct input
        upload=self.client.post('/upload/', data_all_input )
        count_lecture=Lecture.objects.all().count()
        self.assertEqual(1,count_lecture)
        
    def test_error_case_sign_up(self):
        #wrong input
        #no_data is empty data
        #username_only is username only in form data
        #password_only is password and comfirm password only in form data
        data_input={"no_data":{},
            "username_only":{'username':'Time'},
            "password_only":{'password1':'Timetim555', 'password2':'Timetim555'}}
        #correct input
        data_all_input={'username':'Time', 'password1':'Timetim555', 'password2':'Timetim555'}
        
        for i in data_input:
            signup = self.client.post('/signup/',data_input[i])
            count_profile = Profile.objects.all().count()
            self.assertEqual(0,count_profile)
            
        signup = self.client.post('/signup/',data_all_input)
        count_profile = Profile.objects.all().count()
        self.assertEqual(count_profile,1)

    def test_error_case_home(self):
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        #Test no image in lecture
        note_obj=Lecture.objects.create(title="Time", description="time", author=profile)
        Lecture_image.objects.create(lecturekey=note_obj,image=SimpleUploadedFile('666_1.png',
            content=open(BASE_DIR+'/red.png', 'rb').read()))
        response=self.client.post('/',follow=True)
        self.assertTemplateUsed(response,"home.html")
        #Test space in keyword
        response=self.client.get('/',{"keyword_search":"Time"},follow=True)
        self.assertTemplateUsed(response,"searchresult.html")

    def test_error_case_change_password(self):
        user=User.objects.create_user(username='Timmy',password='2542')
        Profile.objects.create(user=user)
        #No user login test
        response_dont_login=self.client.post('/change-password/',{"old_password":"2542" ,
                "new_password1":"TimeTime2542" , 
                "new_password2":"TimeTime2542"}
                ,follow=True
                )
        #it return to login page
        
        self.assertIn("/accounts/login",str(response_dont_login.redirect_chain))


        self.client.post("/accounts/login/",{"username":'Timmy',"password":'2542'})
        data_wrong={
                "wrong_old_password":{"old_password":"Time" ,
                    "new_password1":"TimeTime2542" , 
                    "new_password2":"TimeTime2542"
                    },
                "newpassword_not_valid":{"old_password":"2542"
                    },
                "confirm_password_not_valid":{"old_password":"2542" ,
                    "new_password1":"TimeTime2542"
                    }
                }  
        for i in data_wrong:
            response=self.client.post('/change-password/',data_wrong[i],follow=True)
            #it return to change_password.html
            self.assertTemplateUsed(response,"change_password.html")

    def test_error_case_lecture(self):
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        user=User.objects.create_user(username='Ace',password='2542')
        Profile.objects.create(user=user)
        Lecture.objects.create(title="Time", description="time", author=profile)
        #Test wrongs id
        response=self.client.post("/lecture/Time/2",follow=True)
        self.assertTemplateUsed(response,"page_not_found.html")
        self.assertIn("Please check url or lecture will be delete", str(response.content))
        #Test wrongs title
        response=self.client.post("/lecture/wrong/1",follow=True)
        self.assertTemplateUsed(response,"page_not_found.html")
        self.assertIn("Please check url or lecture will be delete", str(response.content))
        #Test reviews 
        self.client.login(username='Ace',password='2542')
        '''response=self.client.post("/lecture/Time/1",{"review":"Submit"},
                                      follow=True
                                      )
        self.assertIn("submit_review", str(response.content))
        self.assertEqual(response.status_code, 200)'''

    def test_error_case_profile(self):
        user=User.objects.create_user(username='Timmy',password='2542')
        profile=Profile.objects.create(user=user)
        #Test wrongs profile
        response=self.client.post("/profile/Time", follow=True)
        self.assertTemplateUsed(response,"page_not_found.html")
        self.assertIn("Please check username of account in url or account will be delete",
                      str(response.content))
        
        
    def tearDown(self):
        for i in glob.glob(BASE_DIR+'/sandslecture/media/*'):
            i=Path(i)
            for file in i.glob('666*.png'):
                os.remove(file)

        
        


       