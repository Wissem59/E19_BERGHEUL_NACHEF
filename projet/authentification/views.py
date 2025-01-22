from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from .models import CustomUser
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to get the user by email
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            user = None

        # Authenticate user
        if user is not None and user.check_password(password):
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}!")
            return redirect('/home/')  # Redirect to your home or desired page
        else:
            messages.error(request, "Email ou mot de passe incorrect.")

    return render(request, 'authentification/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        form_valid = True

        # Check if password length is between 8 and 20 characters
        if len(password) < 8 or len(password) > 20:
            messages.error(request, "Le mot de passe doit contenir entre 8 et 20 caractères.")
            form_valid = False
        
        # Check if the passwords match
        if password != password_confirm:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            form_valid = False

        # Check if the email is already taken
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
            form_valid = False

        # Create a new user
        if form_valid:
            try:
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                messages.success(request, f"Compte créé avec succès pour {user.username}.")
                return redirect('login')
            except Exception as e:
                messages.error(request, f"Erreur lors de la création du compte : {str(e)}")

    return render(request, 'authentification/signup.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté.")
    return redirect('login')  # Redirect to the login page