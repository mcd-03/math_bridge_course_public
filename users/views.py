from django.shortcuts import render, redirect
from preview.models import Course
from .forms import UserRegisterForm
from django.contrib import messages
from django.contrib import auth

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created; you are now logged in as {username}!')

            user_credentials = auth.authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            auth.login(request, user_credentials)
            return redirect('/courses')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})

def login(request):

    context = {
        'all_courses': Course.objects.all(),
    }

    return render(request, 'users/login.html', context)

def logout(request):
    auth.logout(request)
    messages.info(request, "You've logged out. Thanks for studying today!")
    return redirect('login')