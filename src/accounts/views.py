from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username') or None
        password = request.POST.get('password') or None
        # Check if username and password are provided
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                return render(request, 'auth/login.html', {'error': 'Invalid username or password'})
        else:
            return render(request, 'auth/login.html', {'error': 'Username and password are required'})
    return render(request, 'auth/login.html', {})

def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username') or None
        email = request.POST.get('email') or None
        password = request.POST.get('password') or None
        username = User.objects.filter(username=username).exists()
        email = User.objects.filter(email=email).exists()

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        return redirect("/")
        
