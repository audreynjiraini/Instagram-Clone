from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from .models import *
from django.contrib.auth.models import User
from .forms import NewPostForm, NewProfileForm, NewsLetterForm, CommentForm
from .email import send_welcome_email
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic import RedirectView


# Create your views here.

@login_required(login_url = '/accounts/login/')
def register(request):
    
    return render(request, 'registration/registration_form.html')



def index(request):
    
    form = NewsLetterForm(request.POST)
    
    if request.method == 'POST':
        form = NewsLetterForm(request.POST)
        
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['email']
            
            recipient = NewsLetterRecipients(name = name, email = email)
            recipient.save()
            send_welcome_email(name, email)
            
            return HttpResponseRedirect('/accounts/login/')
        
        else:
            form = NewsLetterForm()
            
    return render(request, 'index.html', {'letterForm': form})



# @login_required(login_url = '/accounts/login/')
# def create_profile(request):
    
#     current_user = request.user
#     if request.method == 'POST':
#         form = NewProfileForm(request.POST, request.FILES)
        
#         if form.is_valid():
#             profile = form.save(commit = False)
#             profile.image_profile = current_user
#             profile.save()
            
#     else:
#         form = NewProfileForm()
        
#     return render(request, 'create_profile.html', {'form': form})
            
            
            
@login_required(login_url = '/accounts/login/')
def new_post(request):
    
    current_user = request.user
    # userProfile = Profile.objects.filter(user = current_user).first()
    
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        
        if form.is_valid():
            image = form.save(commit = False)
            userProfile = Profile.objects.filter(user = current_user).first()
            image.image_profile = userProfile
            image.save()
            
            return redirect('/home')
        
    else:
        form = NewPostForm()
        
    return render(request, 'posts.html', {'form': form})



def home(request):
    
    photos = Image.objects.all()
    people = Profile.objects.all()
    
    current_user = request.user
    userProfile = Profile.objects.filter(user = current_user).first()
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        
        if form.is_valid():
            comments = form.save(commit = False)
            userProfile = Profile.objects.filter(user = current_user).first().user
            image = Image.objects.filter(id = request.POST.get('photo_id')).first()
            
            comments.image_id = image
            comments.profile_id = userProfile
            comments.save_comments()
            
    else:
        form = CommentForm
    
    return render(request, 'home.html', {'people': people, 'photos': photos, 'form': form})



def search_results(request):
    
    if 'username' in request.GET and request.GET["username"]:
        search_term = request.GET.get("username")
        searched_usernames = Profile.search_by_username(search_term)
        
        message = f"{search_term}"
        
        return render(request, 'search.html', {"message": message, "usernames": searched_usernames})
    
    else:
        message = "You haven't searched for any term"
        return render(request, 'search.html', {"message": message})
    
    
    
def comments(request):
    
    current_user = request.user
    userProfile = Profile.objects.filter(user = current_user).first()
    
    if request.method == 'POST':
        form = CommentForm(request.POST, request.FILES)
        
        if form.is_valid():
            comments = form.save(commit = False)
            userProfile = Profile.objects.filter(user = current_user).first().user
            image = Image.objects.filter(id = request.POST.get('photo_id')).first()
            
            comments.image_id = image.id
            comments.profile_id = userProfile
            comments.save_comments()
            
            return redirect('/home')
            
    else:
        form = CommentForm
    
    return render(request, 'comments.html', {'form': form, 'comments': comments})



@login_required(login_url = '/accounts/login/')
def myprofile(request):
    
    current_user = request.user
    image_author = current_user
    # photos = Image.get_by_author(Author)
   
#    if request.method == 'POST':
#        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
#        if form.is_valid():
#            profile = form.save(commit=False)
#            profile.save()
#        return redirect('profile')
#    else:
#        form = ProfileUpdateForm()
       
    return render(request, 'myprofile.html',  {'photos': photos})



def photos(request):
    
    current_user = request.user
    photos = Image.objects.all()
    comments = Image.objects.all().prefetch_related('image_comments')
    
    if current_user.is_authenticated():
        HttpResponseRedirect('index')
    return render(request, 'myprofile.html', {'photos': photos})



def single(request, image_id):
    
    images = Image.objects.get(id = image_id)
    
    try:
        images = Image.objects.get(id = image_id)
        comments = Comment.objects.filter(image_id = images).all()
        
    except Image.DoesNotExist:
        raise Http404("Sorry. The image does not exist.")
    
    return render(request, 'single.html', {'images': images, 'comments': comments})