from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , PasswordChangeForm
from django.contrib.auth import logout, authenticate, login , update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .forms import *
from .models import Lecture,Profile,Lecture_img
from django.forms import modelformset_factory
from django.http import Http404
from django.db.models import Count
from django.contrib import messages
class NoteWithThumbnail:
    def __init__(self, note, thumbnail):
        self.note = note
        self.thumbnail = thumbnail
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            newUser = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            Profile.objects.create(user = newUser)
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
def home(request):
    noteWithThumbnail = []
    latestNote = []
    popularNote = []
    if request.GET.get('word'):
        keyword = request.GET.get('word').lower()
        for note in Lecture.objects.all():
            if keyword in note.title.lower() or keyword in note.description.lower():
                noteWithThumbnail.append(NoteWithThumbnail(note, note.Lecture_img.all()[0]))
        return render(request, 'searchresult.html',{'noteWithThumbnail':noteWithThumbnail})
    else:
        for note in Lecture.objects.all().order_by('-id')[:8][::-1]:
            latestNote.append(NoteWithThumbnail(note, note.Lecture_img.all()[0]))
        
        for note in Lecture.objects.annotate(count=Count('userSaved')).order_by('count')[:8][::-1]:
            popularNote.append(NoteWithThumbnail(note, note.Lecture_img.all()[0]))

        return render(request, 'home.html',{'latestNote':latestNote, 'popularNote':popularNote})

def upload(request):
    if Profile.objects.filter(user=request.user):
        files=[]
        profileObj = Profile.objects.get(user=request.user)
        #ImageFormSet=modelformset_factory(Lecture_img,form=Lecture_imgForms, extra=1)
        if request.method == 'POST':
            
                #for file in request.FILES:
               #files.append(request.FILES['form-0-image'])

            LectureForm = LectureForms(request.POST)
            #Imageform = Lecture_imgForms(request.POST,request.FILES['image'])
            if LectureForm.is_valid():
                LectureForm = LectureForm.save(commit=False)
                LectureForm.author = profileObj
                LectureForm.save()

                for i in request.FILES.getlist('image'):
                    photo = Lecture_img.objects.create(LectureKey=LectureForm , image=i)
                    photo.save()

                # redirect to homepage
                return redirect('/')

            else:
                Error="Please choose your file"

        else:
            LectureForm = LectureForms()
            Error=""
        return render(request, 'upload.html',{'LectureForm': LectureForm,"Error":Error})
    else:
        #Http404("Profile does not found")
        raise Http404("Profile does not found")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST,user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request,form.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user) 
    return render(request,'change_password.html',{'form':form})
def about(request):
    return render(request,'about.html')
def help(request):
    return render(request,'help.html')
def lecture(request,lecture_id):
    if request.method == 'POST':
        profileObj = Profile.objects.get(user = request.user)
        noteObj = Lecture.objects.get(id = int(request.POST.get('noteID')))
        if profileObj not in noteObj.userSaved.all():
            noteObj.userSaved.add(profileObj)
            noteObj.save()
        return HttpResponseRedirect("/" + request.POST.get('noteID'))
    else:
        noteObj = Lecture.objects.get(id = lecture_id)
        imageObjList = noteObj.Lecture_img.all()
        return render(request, 'notedetail.html',{'noteObj': noteObj, "imageObjList": imageObjList})

def profile(request, username):
    userObj = User.objects.get(username = username)
    profileObj = Profile.objects.get(user = userObj)
    if request.method == 'POST':
        form=Profileform(request.POST , request.FILES)
        if form.is_valid():
            profileObj.profilePicture = form.cleaned_data.get('profilePicture')
            profileObj.save()
            
            return HttpResponseRedirect("/profile/"+username)
    else:
        form=Profileform()
        myNote = []
        savedNote = []
        saves = 0
        for note in profileObj.author.all():
            myNote.append(NoteWithThumbnail(note, note.Lecture_img.all()[0]))
            saves += note.userSaved.count()
        for note in Lecture.objects.all():
            if profileObj in note.userSaved.all():
                savedNote.append(NoteWithThumbnail(note, note.Lecture_img.all()[0]))
    return render(request,'profile.html',{'form': form, 'profile': profileObj, 'myNote': myNote, 'savedNote':savedNote, 'saves':saves})

'''List_object_Lecture=[]
List_object_image={}
List_object_image_value_dirt=[]
List_name_img=[]


def upload(request):
    V=0
    found=""
    if Profile.objects.filter(user=request.user):
        Profile_filter=Profile.objects.filter(user=request.user)
        if request.method == 'POST' and 'uploadbutton' in request.POST:
            LectureForms_upload=LectureForms(request.POST)
            Lecture_imgForms_upload = Lecture_imgForms(request.POST,request.FILES)
            if LectureForms_upload.is_valid() and  Lecture_imgForms_upload.is_valid() and request.FILES :
                title_name=LectureForms_upload.cleaned_data.get("title")
                for i in List_object_Lecture:
                    if str(i)==title_name:
                        found=str(i)
                        V+=1

                if V>0 :
                    Lec=LectureForms_upload.save(commit=False)
                    Lec.author=Profile_filter[0]
                    Saveimg=Lecture_imgForms_upload.save()
                    List_object_image_value_dirt.append(Saveimg)
                    #Saveimg.LectureKey=Lec
                    #List_object_image.update({title_name:List_object_image_value_dirt.append(Saveimg)})

                else:
                    Lec=LectureForms_upload.save(commit=False)
                    Lec.author=Profile_filter[0]
                    List_object_Lecture.append(Lec)
                    Saveimg=Lecture_imgForms_upload.save()
                    #Saveimg.LectureKey=Lec
                    List_object_image_value_dirt.append(Saveimg)
                List_name_img.append(Lecture_imgForms_upload.cleaned_data.get("image").name)
                List_object_image.update({title_name:List_object_image_value_dirt})
                return render(request, 'upload.html',{'Image':Lecture_imgForms_upload , 'Lecture':LectureForms_upload, 'L':List_object_Lecture ,"I":List_name_img})
        elif request.method == 'POST' and 'submitbutton' in request.POST:
            
            LectureForms_upload_1=LectureForms(request.POST)
            
            if LectureForms_upload_1.is_valid():
                if List_object_Lecture:
                    title_name=LectureForms_upload_1.cleaned_data.get('title')
                    for i in List_object_Lecture:
                        if str(i)==title_name:
                            i.save()
                            
                            if List_object_image:
                                for P in List_object_image:
                                    if P == title_name:
                                        L=List_object_image[P]
                                        for M in L:
                                            M.LectureKey=i
                                            M.save()
                                List_object_image.pop(title_name)
                            List_object_Lecture.remove(i)
                
            Obj_Lec=Lecture.objects.filter(title=LectureForms_upload_1.cleaned_data.get('title'))
            Img_obj=Lecture_img.objects.all().filter(LectureKey=Obj_Lec[0])
            List_object_Lecture.clear()
            List_object_image.clear()
            List_object_image_value_dirt.clear() 
            List_name_img.clear()
            return render(request, 'lecture.html',{"Lecture_img":Img_obj, 'Lecture':LectureForms_upload_1 })
        else:
            Lecture_imgForms1=Lecture_imgForms()
            LectureForms1=LectureForms()
            return render(request, 'upload.html',{'Image':Lecture_imgForms1 , 'Lecture':LectureForms1})'''