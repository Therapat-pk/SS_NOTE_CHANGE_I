from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , PasswordChangeForm
from django.contrib.auth import logout, authenticate, login , update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.forms import modelformset_factory
from django.http import Http404
from django.db.models import Count
from django.contrib import messages
from .forms import Profileform,LectureForms
from .models import Lecture,Profile,Lecture_image

class NoteWithThumbnail:#It is use college example note (Show about title,example picture,author)

    def __init__(self, note, thumbnail):
        self.note = note
        self.thumbnail = thumbnail


#views area
def signup(request):
    if request.method == 'POST':
        # Django forms
        newuserforms = UserCreationForm(request.POST)       
        print(newuserforms.is_valid())
        if newuserforms.is_valid():
            newuser = newuserforms.save()
            username = newuserforms.cleaned_data.get('username')
            raw_password = newuserforms.cleaned_data.get('password1')
            Profile.objects.create(user=newuser)
            # (authenticate)It verify a new user created 
            # is valid(retune User object) or isn't valid(return None)
            user = authenticate(username=username, password=raw_password)
            # use user(User object that returned) to log in
            login(request, user) 
            return redirect('login')
    else:
        newuserforms = UserCreationForm()
    return render(request, 'signup.html', {'newuserforms': newuserforms})

def home(request):
    noteWithThumbnail = []
    latest_note = []
    popular_note = []
    # a conditional check Is there search?
    if request.GET.get('keyword_search'):
        #keyword_search is input
        keyword = request.GET.get('keyword_search').lower()
        for note in Lecture.objects.all():
            if (keyword in note.title.lower() or keyword in note.description.lower()):
                noteWithThumbnail.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
        return render(request, 'searchresult.html', {'noteWithThumbnail':noteWithThumbnail})
    else:
        #It use to Show 8 lastest note 
        #order_by(-id) is return object ordered by id descending 
        #but really shouldn't [::-1]
        for note in Lecture.objects.all().order_by('-id')[:8][::-1]:
            latest_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
        #It use Show 8 most saved note
        #annotate(count=Count('userSaved')) It use to count each Lecture object
        for note in Lecture.objects.annotate(count=Count('user_saved')).order_by('count')[:8][::-1]:
            popular_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
        return render(request, 'home.html', {'latest_note': latest_note, 'popular_note': popular_note})

def upload(request):
    if Profile.objects.filter(user=request.user):
        files=[]
        profile_obj = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            lecture_forms = LectureForms(request.POST)
            if lecture_forms.is_valid():
                lecture_forms = lecture_forms.save(commit=False)
                lecture_forms.author = profile_obj
                lecture_forms.save()
                # use loop to send output value(The input can Receive multiple image)
                for i in request.FILES.getlist('image'):
                    photo = Lecture_image.objects.create(lecturekey=lecture_forms, image=i)
                    photo.save()
                # redirect to homepage
                return redirect('/')
            else:
                Error="Please choose your file"
        else:
            lecture_forms = LectureForms()
            Error = ""
        return render(request, 'upload.html', {'lecture_forms': lecture_forms, "Error": Error})
    else:
        
        raise Http404("Profile does not found")

def change_password(request):
    if request.method == 'POST':
        pass_change_forms = PasswordChangeForm(data=request.POST, user=request.user)
        if pass_change_forms.is_valid():
            pass_change_forms.save()
            #It user to update user object which the new session will be derived and updates the session appropriately
            #session can temporarily store information like cookie
            update_session_auth_hash(request, pass_change_forms.user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        pass_change_forms = PasswordChangeForm(user=request.user) 
    return render(request, 'change_password.html', {'pass_change_forms': pass_change_forms})

def about(request):
    return render(request, 'about.html')

def help(request):
    return render(request, 'help.html')

def lecture(request, lecture_id):
    #it use to save note
    if (request.method == 'POST' and "noteID" in request.POST):
        profile_obj = Profile.objects.get(user=request.user)
        note_obj = Lecture.objects.get(id=int(request.POST.get('noteID')))
        #Check if user have saved it.
        if profile_obj not in note_obj.user_saved.all():
            note_obj.user_saved.add(profile_obj)
            note_obj.save()
        return HttpResponseRedirect("/" + request.POST.get('noteID'))
    else:
        note_obj = Lecture.objects.get(id=lecture_id)
        image_obj_list = note_obj.Lecture_image.all()
        #confirm is a varible,It use to consider that now is in delete_note form or confirm_delete_note form
        #confirm = False meaning now is in delete_note form
        confirm = False
        #"delete_note" is a name in botton
        if (request.method == 'POST' and "delete_note" in request.POST):
            #confirm = True meaning now is in confirm_delete_note form
            confirm = True
        #"confirm_delete_note" is a name in botton
        elif (request.method == 'POST' and "confirm_delete_note" in request.POST):
            #Delete all Lecture_imge of Lecture object
            image_obj_list.delete()
            #Delete this one Lecture object 
            note_obj.delete()
            return redirect('/')
        return render(request, 'notedetail.html', {'note_obj': note_obj, "image_obj_list": image_obj_list ,"confirm":confirm})

def profile(request, username):
    user_obj = User.objects.get(username=username)
    profile_obj = Profile.objects.get(user=user_obj)
    #Check if user have upload profile picture
    if request.method == 'POST':
        profile_forms=Profileform(request.POST, request.FILES)
        if profile_forms.is_valid():
            profile_obj.profile_picture = profile_forms.cleaned_data.get('profile_picture')
            profile_obj.save()
            return HttpResponseRedirect("/profile/" + username)
    else: 
        profile_forms=Profileform()
        my_note = []
        saved_note = []
        saves = 0
        for note in profile_obj.author.all():
            #It use to collect a note that posted.by user
            my_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
            saves += note.user_saved.count()#Find the sum of all saved users
        for note in Lecture.objects.all():
            #It use to collect a note that saved by user
            if profile_obj in note.user_saved.all():
                saved_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
    return render(request, 'profile.html', {'profile_forms': profile_forms, 'profile': profile_obj, 'my_note': my_note, 'saved_note': saved_note, 'saves': saves})

