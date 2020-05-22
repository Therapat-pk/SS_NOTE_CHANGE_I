from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm , PasswordChangeForm
from django.contrib.auth import logout, authenticate, login , update_session_auth_hash
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect,HttpResponse
from django.forms import modelformset_factory
from django.http import Http404
from django.db.models import Count
from django.contrib import messages
from .forms import Profileform,LectureForms
from .models import Lecture,Profile,Lecture_image,Rate,ErrorReport
from django.urls import reverse

class NoteWithThumbnail:#It is use college example note (Show about title,example picture,author)

    def __init__(self, note, thumbnail):
        self.note = note
        self.thumbnail = thumbnail



#views area
def handler500(request):
    error_report=ErrorReport.objects.order_by('-id')[0]
    return render(request, 'error_500.html',{'error_massage':error_report.error_massage_to_user, 
        'error_views':error_report.error_views})

def signup(request):
    if request.method == 'POST':
        # Django forms
        newuserforms = UserCreationForm(request.POST)       
        if newuserforms.is_valid():
            try:
                newuser = newuserforms.save()
                username = newuserforms.cleaned_data.get('username')
                raw_password = newuserforms.cleaned_data.get('password1')
                Profile.objects.create(user=newuser)
                # (authenticate)It verify a new user created 
                # is valid(retune User object) or isn't valid(return None)
                user = authenticate(username=username, password=raw_password)
                # use user(User object that returned) to log in
                login(request, user) 
                return redirect(reverse("S&S:login")) #redirect('/')
            except:
                ErrorReport.objects.create(error_views="sign up", error_detail="user form",
                    error_massage_to_user="Username or Password isn't valid")
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
        try:
            for note in Lecture.objects.all():
                if (keyword in note.title.lower() or keyword in note.description.lower() or note.Lecture_image.all()):
                    noteWithThumbnail.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
            return render(request, 'searchresult.html', {'noteWithThumbnail':noteWithThumbnail})
        except:
            ErrorReport.objects.create(error_views="home", error_detail="search", 
                error_massage_to_user="Try enter your word to search again")
    else:
        try:
            #It use to Show 8 lastest note 
            #order_by(-id) is return object ordered by id descending 
            #but really shouldn't [::-1]
            for note in Lecture.objects.all().order_by('-id')[:8][::-1]:
                if note.Lecture_image.all():
                    latest_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
        except:
            ErrorReport.objects.create(error_views="home", error_detail="lastest_note", 
                error_massage_to_user="Problem about note")
        try:
            #It use Show 8 most saved note
            #annotate(count=Count('userSaved')) It use to count each Lecture object
            for note in Lecture.objects.annotate(count=Count('user_saved')).order_by('count')[:8][::-1]:
                if note.Lecture_image.all():
                    popular_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
            return render(request, 'home.html', {'latest_note': latest_note, 'popular_note': popular_note})
        except:
            ErrorReport.objects.create(error_views="home", error_detail="popular_note", 
                error_massage_to_user="Problem about note")


def upload(request):
    try:
        profile_obj = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            lecture_forms = LectureForms(request.POST)
            if lecture_forms.is_valid() and request.FILES.get('image'):
                try:
                    lecture_forms = lecture_forms.save(commit=False)
                    lecture_forms.author = profile_obj
                    lecture_forms.save()
                    try:
                        # use loop to send output value(The input can Receive multiple image)
                        for i in request.FILES.getlist('image'):
                            photo = Lecture_image.objects.create(lecturekey=lecture_forms, image=i)
                            photo.save()
                        # redirect to homepage
                        return redirect(reverse("S&S:home"))
                    except:
                        ErrorReport.objects.create(error_views="upload", error_detail="object file image", 
                            error_massage_to_user="Files isn't valid")

                except:
                    ErrorReport.objects.create(error_views="upload", 
                        error_detail="Title or Description isn't valid")
            else:
                choose_files_message='Please choose files'
                    
        else:
            lecture_forms = LectureForms()
            choose_files_message=""
        return render(request, 'upload.html', {'lecture_forms': lecture_forms, 
            'choose_files_message':choose_files_message})
    except:
        ErrorReport.objects.create(error_views="upload", error_detail="Profile object", 
            error_massage_to_user="Problem about profile")

def change_password(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            pass_change_forms = PasswordChangeForm(data=request.POST, user=request.user)
            if pass_change_forms.is_valid():
                try:
                    pass_change_forms.save()
                    #It user to update user object which the new session will be derived and updates the session appropriately
                    #session can temporarily store information like cookie
                    try:
                        update_session_auth_hash(request, pass_change_forms.user)
                        messages.success(request, 'Your password was successfully updated!')
                        return redirect(reverse("S&S:change_password"))
                    except:
                        ErrorReport.objects.create(error_views="change password", error_detail="update_session_auth_hash", 
                            error_massage_to_user="Proble about update password")
                except:
                    ErrorReport.objects.create(error_views="change password", error_detail="pass_change_forms", 
                        error_massage_to_user="Problem about old password or new password isn't valid")
        else:
            pass_change_forms = PasswordChangeForm(user=request.user) 
        return render(request, 'change_password.html', {'pass_change_forms': pass_change_forms})
    else:
        return redirect(reverse("S&S:login"))

def about(request):
    return render(request, 'about.html')

def help(request):
    return render(request, 'help.html')



def lecture(request, lecture_title, lecture_id):
    #it use to save note
    #<QueryDict:{}>
    #<QueryDict:{"{% csrf_token %}":fuenfekfhe ,"save_note":[]}>
    if (request.method == 'POST' and "save_note" in request.POST):
        try:
            profile_obj = Profile.objects.get(user=request.user)
        except:
            ErrorReport.objects.create(error_views="lecture", error_detail="profile objects", 
                error_massage_to_user="Problem about your profile")
        try:
            note_obj = Lecture.objects.get(id=int(request.POST.get('save_note')))
            #Check if user have saved it.
            if profile_obj not in note_obj.user_saved.all():
                note_obj.user_saved.add(profile_obj)
                note_obj.save()
            return HttpResponseRedirect(reverse('S&S:lecture',args=[note_obj.title,note_obj.id]))
        except:
            ErrorReport.objects.create(error_views="lecture", error_detail="note objects", 
                error_massage_to_user="Problem about this note")
    else:
        profile=None
        if request.user.is_authenticated:
            profile=Profile.objects.get(user=request.user)
        try:
            note_obj = Lecture.objects.get(id=lecture_id)
            #Check title match url
            if (note_obj.title!=lecture_title):
                error_massage = "Please check url or lecture will be delete"
                return render(request,"page_not_found.html",{"error_massage":error_massage})
            image_obj_list = note_obj.Lecture_image.all()
            #confirm is a varible,It use to consider that now is in delete_note form or confirm_delete_note form
            #confirm = False meaning now is in delete_note form
            confirm = False
            comment = False
            rate_list=[]
            total_point=0
            try:
                #"delete_note" is a name in botton
                if ( request.method == 'POST' and "delete_note" in request.POST):
                    #confirm = True meaning now is in confirm_delete_note form
                    confirm = True
                #"confirm_delete_note" is a name in botton
                elif (request.method == 'POST' and "confirm_delete_note" in request.POST):
                    #Delete all Lecture_imge of Lecture object
                    image_obj_list.delete()
                    #Delete this one Lecture object 
                    note_obj.delete()
                    return redirect(reverse("S&S:home"))
                try:
                    if (request.method == 'POST' and "review" in request.POST):
                        comment=True
                    elif (request.method == 'POST' and "submit_review" in request.POST):
                        point=request.POST.get("point")
                        comment=request.POST.get("text_comment")
                        #user=request.POST.get("submit_review")
                        
                        rate=Rate.objects.create(rate=point,comment=comment,lecture_rate=note_obj,user_rate=profile)
                        comment=True
                    try:
                        for i in Rate.objects.all():
                            if i.lecture_rate == note_obj:
                                rate_list.append(i)
                                if i.rate != None:
                                    total_point += i.rate
                    except:
                        ErrorReport.objects.create(error_views="lecture", 
                            error_detail="for in rate (rate list, total point", 
                            error_massage_to_user="Problem about review")
                except:
                    ErrorReport.objects.create(error_views="lecture",
                        error_detail="review",
                        error_massage_to_user="Problem about Point or comment isn't valid")
            except:
                ErrorReport.objects.create(error_views="lecture", 
                    error_detail="delete note",
                    error_massage_to_user="Problem about Delete note")
        except:
            ErrorReport.objects.create(error_views="lecture", 
                error_detail="note_obj or image_obj_list",
                error_massage_to_user="Problem about this note isn't valid")
            error_massage = "Please check url or lecture will be delete"
            return render(request,"page_not_found.html",{"error_massage":error_massage})
                
        
        
        return render(request, 'notedetail.html', {'note_obj': note_obj, "image_obj_list": image_obj_list, "confirm":confirm,
            'comment':comment, "ratedetail":rate_list ,"ratedetail_length":len(rate_list),
            "profile_request":profile, "total_point":total_point})

def profile(request, username):
    try:
        user_obj = User.objects.get(username=username)
        profile_obj = Profile.objects.get(user=user_obj)
        #Check if user have upload profile picture
        if request.method == 'POST':
            profile_forms=Profileform(request.POST, request.FILES)
            if profile_forms.is_valid():
                try:
                    profile_obj.profile_picture = profile_forms.cleaned_data.get('profile_picture')
                    profile_obj.save()
                    return HttpResponseRedirect((reverse("S&S:profile",args=[username])))
                except:
                    ErrorReport.objects.create(error_views="profile", error_detail="profile_pic form"
                        ,error_massage_to_user="profile pic isn't valid")
        else: 
            profile_forms=Profileform()
            my_note = []
            saved_note = []
            saves = 0
            try:
                for note in profile_obj.author.all():
                    #It use to collect a note that posted.by user
                    my_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
                    saves += note.user_saved.count()#Find the sum of all saved users
            except:
                ErrorReport.objects.create(error_views="profile", error_detail="mynote"
                    ,error_massage_to_user="Problem about your note")
            try:    
                for note in Lecture.objects.all():
                    #It use to collect a note that saved by user
                    if profile_obj in note.user_saved.all():
                        saved_note.append(NoteWithThumbnail(note, note.Lecture_image.all()[0]))
            except:
                ErrorReport.objects.create(error_views="profile", error_detail="saved note"
                    ,error_massage_to_user="Problem about your saved note")
        return render(request, 'profile.html', {'profile_forms': profile_forms, 
            'profile': profile_obj,
            'my_note': my_note, 'saved_note': saved_note,
            'saves': saves})
    except:
        ErrorReport.objects.create(error_views="profile", error_detail="user_object"
            ,error_massage_to_user="Problem about your user")
        error_massage = "Please check username of account in url or account will be delete"
        return render(request,"page_not_found.html",{"error_massage":error_massage})
